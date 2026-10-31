"""Commands that test a finished run or the pipeline itself: robustness, feedback value, noise."""

from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from autograde.cli.common import (
    load_run,
    load_run_with_feedback,
    read_setup,
    records_for,
    run_dir,
    run_pipeline,
    stored_rubrics,
    write_json,
    write_lines,
)
from autograde.config import Settings
from autograde.datasets import LOADERS, load_dataset, select
from autograde.evaluation.calibrate import calibrate
from autograde.evaluation.cascade import cascade_report
from autograde.evaluation.compliance import compliance
from autograde.evaluation.criteria import criteria_report
from autograde.evaluation.feedback_ab import lost_marks, run_ab, table
from autograde.evaluation.judge_check import agreement, export_sheet, write_sheet
from autograde.evaluation.revision import revision_test, summarise
from autograde.evaluation.robustness import NAMES, robustness_test
from autograde.evaluation.robustness import summarise as robustness_summary
from autograde.evaluation.sensitivity import compare_runs
from autograde.evaluation.stress import Case, build_cases, run_stress
from autograde.evaluation.stress import summarise as summarise_stress
from autograde.evaluation.transfer import summarise as summarise_transfer
from autograde.evaluation.transfer import transfer_test
from autograde.evaluation.voting import review_report, vote_report
from autograde.llm import build_client
from autograde.pipeline.baseline import grade_baseline
from autograde.pipeline.review import review_stats
from autograde.pipeline.rubric import store_for
from autograde.pipeline.run import mark_item, to_question
from autograde.viewer.build import sample_by_mark


def register(sub) -> None:
    """Add the evaluation commands (stress, robustness, review, ...) to the subparsers."""
    st = sub.add_parser("stress", help="robustness test on answers with a known right outcome")
    st.add_argument("--dataset", required=True, choices=sorted(LOADERS))
    st.add_argument("--split", default="dev", choices=["dev", "test"])
    st.add_argument("--pool", type=int, default=60, help="answers to draw the cases from")
    st.add_argument("--per-kind", type=int, default=6)
    st.add_argument("--seed", type=int, default=0)
    st.add_argument("--mode", default="pipeline", choices=["pipeline", "baseline"])
    st.add_argument("--name", required=True)
    st.set_defaults(func=cmd_stress)

    tr = sub.add_parser("transfer", help="does the feedback help on a different question")
    tr.add_argument("--name", required=True)
    tr.add_argument("--sample", type=int, help="test only N answers, spread over the marks")
    tr.set_defaults(func=cmd_transfer)

    rv = sub.add_parser("revision", help="test whether the feedback helps a student improve")
    rv.add_argument("--name", required=True)
    rv.add_argument("--sample", type=int, help="test only N answers, spread over the marks")
    rv.add_argument(
        "--own-knowledge",
        action="store_true",
        help="the student may also use what they know, not only the feedback",
    )
    rv.set_defaults(func=cmd_revision)

    ab = sub.add_parser(
        "feedback-ab", help="feedback from the marking vs feedback from the answers alone"
    )
    ab.add_argument("--name", required=True, help="a finished marking run")
    ab.add_argument("--sample", type=int, help="test only N answers, spread over the marks")
    ab.set_defaults(func=cmd_feedback_ab)

    rw = sub.add_parser("review", help="which answers are worth a look, and are they worse")
    rw.add_argument("--name", required=True)
    rw.set_defaults(func=cmd_review)

    rb = sub.add_parser(
        "robustness", help="do marks hold when the same answer is written differently"
    )
    rb.add_argument("--name", required=True, help="a finished marking run")
    rb.add_argument("--perturb", nargs="+", default=list(NAMES), choices=NAMES)
    rb.add_argument("--sample", type=int, help="test only N answers, spread over the marks")
    rb.add_argument("--seed", type=int, default=0)
    rb.set_defaults(func=cmd_robustness)

    js = sub.add_parser("judge-sheet", help="a sheet for a person to check the feedback judge")
    js.add_argument("--runs", nargs="+", required=True, help="runs that were judged")
    js.add_argument("--per-run", type=int, default=10)
    js.add_argument("--seed", type=int, default=0)
    js.add_argument("--out", type=Path, required=True)
    js.set_defaults(func=cmd_judge_sheet)

    ja = sub.add_parser("judge-agreement", help="judge vs the person's answers on that sheet")
    ja.add_argument("--sheet", type=Path, required=True)
    ja.set_defaults(func=cmd_judge_agreement)

    vt = sub.add_parser("votes", help="how steady is the grader, and does voting help")
    vt.add_argument("--name", required=True)
    vt.set_defaults(
        func=lambda a, s: print(
            json.dumps(
                {
                    "voting": vote_report(load_run(s, a.name)),
                    "review": review_report(load_run(s, a.name)),
                },
                indent=2,
            )
        )
    )

    sn = sub.add_parser("sensitivity", help="how far did marks move between two runs")
    sn.add_argument("--a", required=True, help="original run")
    sn.add_argument("--b", required=True, help="changed run")
    sn.set_defaults(
        func=lambda a, s: print(
            json.dumps(compare_runs(load_run(s, a.a), load_run(s, a.b)), indent=2)
        )
    )

    cr = sub.add_parser("criteria", help="criterion-by-criterion agreement with the teacher")
    cr.add_argument("--name", required=True)
    cr.set_defaults(
        func=lambda a, s: print(json.dumps(criteria_report(load_run(s, a.name)), indent=2))
    )

    ca = sub.add_parser("calibrate", help="fit partial-credit weight and stretch to teacher marks")
    ca.add_argument("--name", required=True, help="a finished pipeline run with teacher marks")
    ca.set_defaults(func=cmd_calibrate)

    cs = sub.add_parser("cascade", help="what-if: re-mark unsure answers with a stronger run")
    cs.add_argument("--cheap", required=True, help="finished run of the cheap model")
    cs.add_argument("--strong", required=True, help="finished run of the strong model")
    cs.set_defaults(
        func=lambda a, s: print(
            json.dumps(cascade_report(load_run(s, a.cheap), load_run(s, a.strong)), indent=1)
        )
    )

    co = sub.add_parser("compliance", help="do marks and feedback move with rubric strictness")
    co.add_argument(
        "--run", action="append", required=True, metavar="LEVEL=RUN",
        help="repeat once per level, for example lenient=dk_lenient",
    )  # fmt: skip
    co.set_defaults(func=cmd_compliance)


def cmd_calibrate(args: argparse.Namespace, settings: Settings) -> None:
    """Fit the partial-credit weight and stretch to teacher marks and print them."""
    results = load_run(settings, args.name)
    rubrics = stored_rubrics(results, settings, read_setup(run_dir(settings, args.name)))
    print(json.dumps(calibrate(results, rubrics), indent=2))


def cmd_compliance(args: argparse.Namespace, settings: Settings) -> None:
    """Print whether marks and feedback move with rubric strictness, one run per level."""
    runs = {}
    for spec in args.run:
        level, _, name = spec.partition("=")
        runs[level] = load_run(settings, name)
    print(json.dumps(compliance(runs), indent=2))


def cmd_stress(args: argparse.Namespace, settings: Settings) -> None:
    """Test the marker on built-to-order good and bad answers and print the summary."""
    items = select(
        load_dataset(args.dataset, settings.paths.data_dir), args.split, args.pool, args.seed
    )
    run = run_dir(settings, args.name)
    run.mkdir(parents=True, exist_ok=True)
    cases_path = (
        settings.paths.runs_dir
        / f"stress_cases_{args.dataset}_{args.split}_{args.seed}_{args.pool}_{args.per_kind}.json"
    )
    if cases_path.exists():  # reuse, so every method faces the same cases
        cases = [Case.model_validate(c) for c in json.loads(cases_path.read_text(encoding="utf-8"))]
    else:
        cases = build_cases(items, args.per_kind, args.seed, build_client(settings.student))
        cases_path.write_text(
            json.dumps([c.model_dump() for c in cases], indent=1), encoding="utf-8"
        )
    grader = build_client(settings.llm)
    if args.mode == "baseline":

        def mark(item):
            return grade_baseline(item, grader).predicted_mark

    else:
        cfg = settings.pipeline
        store = store_for(settings, grader=grader)
        questions = {c.item.question_key: to_question(c.item) for c in cases}
        with ThreadPoolExecutor(cfg.max_workers) as pool:
            records = dict(zip(questions, pool.map(store.get, questions.values()), strict=True))

        def mark(item):
            return mark_item(item, records[item.question_key], grader, cfg).grading.total

    rows = run_stress(cases, mark, settings.pipeline.max_workers)
    out = {"mode": args.mode, **summarise_stress(rows), "cost_usd": round(grader.usage.cost_usd, 3)}
    write_json(run / "stress.json", {**out, "rows": rows})
    print(json.dumps(out, indent=2))


def cmd_transfer(args: argparse.Namespace, settings: Settings) -> None:
    """Test whether a student model improves its answer by using the feedback."""
    run = run_dir(settings, args.name)
    results = load_run_with_feedback(settings, args.name, args.sample)
    grader, student = build_client(settings.llm), build_client(settings.student)
    rows = transfer_test(
        results, grader, student, grader, settings.paths.runs_dir, settings.pipeline.max_workers
    )
    out = {
        **summarise_transfer(rows),
        "cost_usd": round(grader.usage.cost_usd + student.usage.cost_usd, 3),
    }
    sfx = "_sample" if args.sample else ""
    write_lines(run / f"transfer_rows{sfx}.jsonl", [r.model_dump_json() for r in rows])
    write_json(run / f"transfer_scores{sfx}.json", out)
    print(json.dumps(out, indent=2))


def cmd_robustness(args: argparse.Namespace, settings: Settings) -> None:
    """Re-mark rewritten answers against a re-marking control and print the shifts."""
    run = run_dir(settings, args.name)
    results = [r for r in load_run(settings, args.name) if r.grading]
    if args.sample:
        results = sample_by_mark(results, args.sample)
    cfg = run_pipeline(run, settings)
    grader, writer = build_client(settings.llm), build_client(settings.llm)
    shifts = robustness_test(
        results,
        records_for(results, settings, cfg),
        grader,
        writer,
        cfg,
        args.perturb,
        settings.paths.runs_dir / "robustness_cache.json",
        args.seed,
        settings.pipeline.max_workers,
    )
    table = robustness_summary(shifts)
    write_json(run / "robustness.json", table)
    print(json.dumps(table, indent=1))


def cmd_review(args: argparse.Namespace, settings: Settings) -> None:
    """Print which answers of a run are worth a person's look."""
    print(json.dumps(review_stats(load_run(settings, args.name)), indent=2))


def cmd_judge_sheet(args: argparse.Namespace, settings: Settings) -> None:
    """Write the sheet a person fills in to check the feedback judge."""
    rows = export_sheet(settings.paths.runs_dir, args.runs, args.per_run, args.seed)
    write_sheet(rows, args.out)
    print(f"wrote {len(rows)} rows to {args.out}; fill the human_* columns with y or n")


def cmd_judge_agreement(args: argparse.Namespace, settings: Settings) -> None:
    """Print how far the feedback judge agrees with a person's filled-in sheet."""
    print(json.dumps(agreement(args.sheet), indent=2))


def cmd_revision(args: argparse.Namespace, settings: Settings) -> None:
    """Test whether a student who revises with the feedback gains marks."""
    run = run_dir(settings, args.name)
    results = load_run_with_feedback(settings, args.name, args.sample)
    cfg = run_pipeline(run, settings)
    grader, student = build_client(settings.llm), build_client(settings.student)
    rows = revision_test(
        results,
        records_for(results, settings, cfg),
        grader,
        student,
        cfg,
        settings.paths.runs_dir / "revision_control2.json",
        settings.pipeline.max_workers,
        own_knowledge=args.own_knowledge,
    )
    out = {
        **summarise(rows),
        "cost_usd": round(grader.usage.cost_usd + student.usage.cost_usd, 3),
    }
    sfx = ("_own" if args.own_knowledge else "") + ("_sample" if args.sample else "")
    write_lines(run / f"revision_rows{sfx}.jsonl", [r.model_dump_json() for r in rows])
    write_json(run / f"revision_scores{sfx}.json", out)
    print(json.dumps(out, indent=2))


def cmd_feedback_ab(args: argparse.Namespace, settings: Settings) -> None:
    """`llm` marks and grades every rewrite; `student` is the second model family."""
    run = run_dir(settings, args.name)
    results = lost_marks(load_run(settings, args.name))
    if args.sample:
        results = sample_by_mark(results, args.sample)
    if not results:
        sys.exit("No marked answers that lost marks in that run.")
    cfg = run_pipeline(run, settings)
    grader, other = build_client(settings.llm), build_client(settings.student)
    report = run_ab(
        results,
        records_for(results, settings, cfg),
        grader,
        other,
        cfg,
        run / "feedback_ab",
        settings.paths.runs_dir,
        settings.pipeline.max_workers,
    )
    report["cost_usd"] = {
        grader.name: round(grader.usage.cost_usd, 3),
        other.name: round(other.usage.cost_usd, 3),
    }
    write_json(run / "feedback_ab" / "scores.json", report)
    text = table(report)
    (run / "feedback_ab" / "table.md").write_text(text + "\n", encoding="utf-8")
    print(text)
    print("cost:", report["cost_usd"])

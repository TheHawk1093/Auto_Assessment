"""Commands that test a finished run or the pipeline itself: robustness, feedback value, noise."""

from __future__ import annotations

import argparse
import json
from concurrent.futures import ThreadPoolExecutor

from autograde.cli.common import (
    load_run,
    load_run_with_feedback,
    records_for,
    run_dir,
    run_pipeline,
    write_json,
    write_lines,
)
from autograde.config import Settings
from autograde.datasets import LOADERS, load_dataset, select
from autograde.evaluation.compliance import compliance
from autograde.evaluation.criteria import criteria_report
from autograde.evaluation.revision import revision_test, summarise
from autograde.evaluation.sensitivity import compare_runs
from autograde.evaluation.stress import Case, build_cases, run_stress
from autograde.evaluation.stress import summarise as summarise_stress
from autograde.evaluation.transfer import summarise as summarise_transfer
from autograde.evaluation.transfer import transfer_test
from autograde.evaluation.voting import review_report, vote_report
from autograde.llm import build_client
from autograde.pipeline.baseline import grade_baseline
from autograde.pipeline.rubric import RubricStore
from autograde.pipeline.run import mark_item, to_question


def register(sub) -> None:
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
    rv.set_defaults(func=cmd_revision)

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

    co = sub.add_parser("compliance", help="do marks and feedback move with rubric strictness")
    co.add_argument(
        "--run", action="append", required=True, metavar="LEVEL=RUN",
        help="repeat once per level, for example lenient=dk_lenient",
    )  # fmt: skip
    co.set_defaults(func=cmd_compliance)


def cmd_compliance(args: argparse.Namespace, settings: Settings) -> None:
    runs = {}
    for spec in args.run:
        level, _, name = spec.partition("=")
        runs[level] = load_run(settings, name)
    print(json.dumps(compliance(runs), indent=2))


def cmd_stress(args: argparse.Namespace, settings: Settings) -> None:
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
        store = RubricStore(
            settings.paths.rubrics_dir, grader, cfg.rubric_selftest, cfg.rubric_variant
        )
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


def cmd_revision(args: argparse.Namespace, settings: Settings) -> None:
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
    )
    out = {
        **summarise(rows),
        "cost_usd": round(grader.usage.cost_usd + student.usage.cost_usd, 3),
    }
    sfx = "_sample" if args.sample else ""
    write_lines(run / f"revision_rows{sfx}.jsonl", [r.model_dump_json() for r in rows])
    write_json(run / f"revision_scores{sfx}.json", out)
    print(json.dumps(out, indent=2))

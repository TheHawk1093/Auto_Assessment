"""Command line: download data, run the grader, judge feedback, print a report."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from autograde.config import PipelineConfig, Settings, load_settings
from autograde.datasets import LOADERS, load_dataset, select
from autograde.datasets.download import download_all, download_engsaf
from autograde.datasets.perturb import perturb_items
from autograde.evaluation.experiments import (
    comparisons,
    prompt_fingerprint,
    read_log,
    record_run,
)
from autograde.evaluation.judge import judge_all, pass_rates
from autograde.evaluation.metrics import report
from autograde.evaluation.revision import revision_test, summarise
from autograde.evaluation.sensitivity import compare_runs
from autograde.evaluation.stress import Case, build_cases, run_stress
from autograde.evaluation.stress import summarise as summarise_stress
from autograde.evaluation.transfer import summarise as summarise_transfer
from autograde.evaluation.transfer import transfer_test
from autograde.evaluation.voting import review_report, vote_report
from autograde.llm import build_client
from autograde.pipeline.baseline import grade_baseline
from autograde.pipeline.feedback import write_feedback
from autograde.pipeline.rescore import rescore
from autograde.pipeline.rubric import RubricStore, cached_record
from autograde.pipeline.run import mark_item, read_results, run_items, to_question
from autograde.vcs import GitError, commit_experiment, history
from autograde.viewer import sample_by_mark, sample_spread, write_report
from autograde.viewer.compare import Tab, write_compare
from autograde.viewer.compare import build_data as build_compare_data

log = logging.getLogger("autograde")


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="autograde", description=__doc__)
    p.add_argument("--config", type=Path, help="YAML settings (default: configs/default.yaml)")
    sub = p.add_subparsers(dest="cmd", required=True)

    dl = sub.add_parser("download", help="fetch the stage-1 datasets into data/raw")
    dl.add_argument("--engsaf", action="store_true", help="also fetch EngSAF (benchmark only)")

    run = sub.add_parser("run", help="grade a sample of answers")
    run.add_argument("--dataset", required=True, choices=sorted(LOADERS))
    run.add_argument("--split", default="dev", choices=["dev", "test"])
    run.add_argument("-n", type=int, default=20, help="sample size (omit for the whole split)")
    run.add_argument("--all", action="store_true", help="use the whole split")
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--mode", default="pipeline", choices=["pipeline", "baseline"])
    run.add_argument("--name", required=True, help="run folder name under runs/")
    run.add_argument("--variant", help="label for this design in the experiment log")
    run.add_argument("--note", default="", help="one line on what this variant changes")
    run.add_argument("--no-commit", action="store_true", help="skip the git commit and tag")
    run.add_argument(
        "--perturb-model", metavar="SPEC",
        help="alter model answers: mask<percent> blanks words, short<percent> keeps the start",
    )  # fmt: skip

    judge = sub.add_parser("judge", help="score the feedback of a finished run")
    judge.add_argument("--name", required=True)

    rep = sub.add_parser("report", help="print metrics for a finished run")
    rep.add_argument("--name", required=True)

    rs = sub.add_parser(
        "rescore", help="re-price a finished run's verdicts with another partial weight (free)"
    )
    rs.add_argument("--name", required=True, help="source run")
    rs.add_argument("--new-name", required=True)
    rs.add_argument("--partial-weight", type=float, required=True)
    rs.add_argument("--variant", required=True)
    rs.add_argument("--note", default="")
    rs.add_argument("--no-commit", action="store_true")

    rf = sub.add_parser(
        "refeedback", help="rewrite the feedback of a finished run; marks stay the same"
    )
    rf.add_argument("--name", required=True, help="source run")
    rf.add_argument("--new-name", required=True)
    rf.add_argument(
        "--feedback", choices=["standard", "hints", "critique", "formal"], required=True
    )
    rf.add_argument("--n", type=int, default=1, help="drafts to write; the best is kept")
    rf.add_argument("--variant", required=True)
    rf.add_argument("--note", default="")
    rf.add_argument("--no-commit", action="store_true")

    sn = sub.add_parser("sensitivity", help="how far did marks move between two runs")
    sn.add_argument("--a", required=True, help="original run")
    sn.add_argument("--b", required=True, help="changed run")

    st = sub.add_parser("stress", help="robustness test on answers with a known right outcome")
    st.add_argument("--dataset", required=True, choices=sorted(LOADERS))
    st.add_argument("--split", default="dev", choices=["dev", "test"])
    st.add_argument("--pool", type=int, default=60, help="answers to draw the cases from")
    st.add_argument("--per-kind", type=int, default=6)
    st.add_argument("--seed", type=int, default=0)
    st.add_argument("--mode", default="pipeline", choices=["pipeline", "baseline"])
    st.add_argument("--name", required=True)

    tr = sub.add_parser("transfer", help="does the feedback help on a different question")
    tr.add_argument("--name", required=True)
    tr.add_argument("--sample", type=int, help="test only N answers, spread over the marks")

    vt = sub.add_parser("votes", help="how steady is the grader, and does voting help")
    vt.add_argument("--name", required=True)

    rv = sub.add_parser("revision", help="test whether the feedback helps a student improve")
    rv.add_argument("--name", required=True)
    rv.add_argument("--sample", type=int, help="test only N answers, spread over the marks")

    cp = sub.add_parser("compare", help="one page, one tab per run, the same N answers in each")
    cp.add_argument(
        "--run", action="append", required=True, metavar="NAME=LABEL|SHORT|DESCRIPTION",
        help="repeat once per tab; the first run decides which answers are shown",
    )  # fmt: skip
    cp.add_argument("--limit", type=int, default=5)
    cp.add_argument("--title", default="Method comparison")
    cp.add_argument("--out", required=True, help="folder name under runs/")

    logp = sub.add_parser("log", help="add a finished run to experiments/log.jsonl")
    logp.add_argument("--name", required=True)
    logp.add_argument("--variant", required=True)
    logp.add_argument("--note", default="")

    sub.add_parser("history", help="list experiment tags with their scores")

    view = sub.add_parser("view", help="(re)build runs/<name>/report.html to read the samples")
    view.add_argument("--name", required=True)
    view.add_argument("--limit", type=int, help="show only N answers, spread over questions")
    view.add_argument("--seed", type=int, default=0)
    return p


def _write_view(
    run_dir: Path, settings: Settings, limit: int | None = None, seed: int = 0, by: str = "question"
) -> Path:
    """Build report.html from a run folder: answers, marks, quotes, feedback, judgements."""
    setup_path = run_dir / "run.json"
    llm = json.loads(setup_path.read_text(encoding="utf-8"))["llm"] if setup_path.exists() else {}
    client_name = (
        f"{llm.get('backend', settings.llm.backend)}-{llm.get('model', settings.llm.model)}"
    )
    if llm.get("effort"):
        client_name += f"-{llm['effort']}"
    judged = {}
    jpath = run_dir / "feedback_judgements.jsonl"
    if jpath.exists():
        for line in jpath.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            judged[row.pop("id")] = row
    results = read_results(run_dir / "results.jsonl")
    if limit:
        results = (
            sample_by_mark(results, limit) if by == "mark" else sample_spread(results, limit, seed)
        )
    info = {}
    if setup_path.exists():
        setup = json.loads(setup_path.read_text(encoding="utf-8"))
        info = {
            "variant": setup.get("variant"),
            "mode": setup.get("mode"),
            "model": client_name,
            "prompts": prompt_fingerprint()["all"],
            "settings": setup.get("pipeline", {}) if setup.get("mode") == "pipeline" else {},
        }
    return write_report(
        results,
        run_dir / ("report_sample.html" if limit else "report.html"),
        run_dir.name + (f" (sample of {len(results)})" if limit else ""),
        settings.paths.cache_dir,
        client_name,
        judged,
        info,
    )


def _cmd_run(args: argparse.Namespace, settings: Settings) -> None:
    items = select(
        load_dataset(args.dataset, settings.paths.data_dir),
        args.split,
        None if args.all else args.n,
        args.seed,
    )
    if args.perturb_model:
        items = perturb_items(items, args.perturb_model, args.seed)
    run_dir = settings.paths.runs_dir / args.name
    run_dir.mkdir(parents=True, exist_ok=True)
    client = build_client(settings.llm)
    setup = {
        "perturb_model": args.perturb_model,
        "dataset": args.dataset,
        "split": args.split,
        "n": len(items),
        "seed": args.seed,
        "mode": args.mode,
        "variant": args.variant or args.mode,
        "llm": settings.llm.model_dump(),
        "pipeline": settings.pipeline.model_dump(),
    }
    (run_dir / "run.json").write_text(json.dumps(setup, indent=2), encoding="utf-8")
    results = run_items(
        items,
        args.mode,
        client,
        settings,
        run_dir / "results.jsonl",
        progress=lambda n, total: log.info("graded %d/%d", n, total),
    )
    _finish(run_dir, results, client.usage.as_dict(), settings, args)


def _finish(
    run_dir: Path, results: list, usage: dict, settings: Settings, args: argparse.Namespace
) -> None:
    """Score against the teacher, write the report, log the run, commit and tag."""
    summary = report(results)
    (run_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (run_dir / "usage.json").write_text(json.dumps(usage, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    print("usage:", usage)
    print("report:", _write_view(run_dir, settings))
    print("logged:", record_run(run_dir, args.variant or args.mode, args.note))
    if not args.no_commit:
        entries = read_log()
        vs_base, vs_prev = comparisons(entries, len(entries) - 1)
        try:
            print("committed and tagged:", commit_experiment(entries[-1], vs_base, vs_prev))
        except GitError as exc:
            print("git step skipped:", exc)


def _cmd_rescore(args: argparse.Namespace, settings: Settings) -> None:
    src = settings.paths.runs_dir / args.name
    dst = settings.paths.runs_dir / args.new_name
    setup = json.loads((src / "run.json").read_text(encoding="utf-8"))
    if setup["mode"] != "pipeline":
        sys.exit("Only pipeline runs have verdicts to re-price.")
    client_name = f"{setup['llm']['backend']}-{setup['llm']['model']}"
    if setup["llm"].get("effort"):
        client_name += f"-{setup['llm']['effort']}"
    variant = setup.get("pipeline", {}).get("rubric_variant", "generated")
    results = read_results(src / "results.jsonl")
    rubrics = {}
    for r in results:
        rec = cached_record(settings.paths.cache_dir, client_name, r.item.question_key, variant)
        if rec is None:
            sys.exit(f"No cached marking scheme for {r.item.question_key}.")
        rubrics[r.item.question_key] = rec.rubric
    new = rescore(results, rubrics, args.partial_weight)
    dst.mkdir(parents=True, exist_ok=True)
    setup["variant"] = args.variant
    setup["pipeline"] = {
        **setup["pipeline"],
        "mark_rule": "status",
        "partial_weight": args.partial_weight,
        "rescored_from": args.name,
    }
    (dst / "run.json").write_text(json.dumps(setup, indent=2), encoding="utf-8")
    (dst / "results.jsonl").write_text(
        "\n".join(r.model_dump_json() for r in new) + "\n", encoding="utf-8"
    )
    zero = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
    _finish(dst, new, zero, settings, args)


def _run_pipeline(run_dir: Path, settings: Settings) -> PipelineConfig:
    """The pipeline settings a run was made with (falls back to the current config)."""
    path = run_dir / "run.json"
    if path.exists():
        saved = json.loads(path.read_text(encoding="utf-8")).get("pipeline")
        if saved:
            return PipelineConfig.model_validate(saved)
    return settings.pipeline


def _records(results: list, settings: Settings, cfg: PipelineConfig | None = None) -> dict:
    """Cached marking schemes for the questions in `results` (same cache path as the run)."""
    cfg = cfg or settings.pipeline
    store = RubricStore(
        settings.paths.cache_dir,
        build_client(settings.llm),
        cfg.rubric_selftest,
        cfg.rubric_variant,
    )
    return {r.item.question_key: store.get(to_question(r.item)) for r in results}


def _cmd_refeedback(args: argparse.Namespace, settings: Settings) -> None:
    src = settings.paths.runs_dir / args.name
    dst = settings.paths.runs_dir / args.new_name
    setup = json.loads((src / "run.json").read_text(encoding="utf-8"))
    results = read_results(src / "results.jsonl")
    records = _records(results, settings)
    client = build_client(settings.llm)

    def redo(r):
        if r.grading is None:
            return r
        rubric = records[r.item.question_key].rubric
        fb = write_feedback(r.item, rubric, r.grading, client, args.feedback, args.n)
        return r.model_copy(update={"feedback": fb})

    with ThreadPoolExecutor(settings.pipeline.max_workers) as pool:
        new = list(pool.map(redo, results))
    dst.mkdir(parents=True, exist_ok=True)
    setup["variant"] = args.variant
    setup["pipeline"] = {
        **setup["pipeline"],
        "feedback_variant": args.feedback,
        "refeedback_from": args.name,
    }
    (dst / "run.json").write_text(json.dumps(setup, indent=2), encoding="utf-8")
    (dst / "results.jsonl").write_text(
        "\n".join(r.model_dump_json() for r in new) + "\n", encoding="utf-8"
    )
    _finish(dst, new, client.usage.as_dict(), settings, args)


def _cmd_revision(args: argparse.Namespace, settings: Settings) -> None:
    run_dir = settings.paths.runs_dir / args.name
    results = [r for r in read_results(run_dir / "results.jsonl") if r.feedback]
    if not results:
        sys.exit("No results with feedback in that run.")
    if args.sample:
        results = sample_by_mark(results, args.sample)
    sfx = "_sample" if args.sample else ""
    cfg = _run_pipeline(run_dir, settings)
    grader, student = build_client(settings.llm), build_client(settings.student)
    rows = revision_test(
        results,
        _records(results, settings, cfg),
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
    (run_dir / f"revision_rows{sfx}.jsonl").write_text(
        "\n".join(r.model_dump_json() for r in rows), encoding="utf-8"
    )
    (run_dir / f"revision_scores{sfx}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def _cmd_compare(args: argparse.Namespace, settings: Settings) -> None:
    tabs = []
    for spec in args.run:
        run, _, rest = spec.partition("=")
        label, _, rest = rest.partition("|")
        short, _, desc = rest.partition("|")
        tabs.append(Tab(run, label or run, short, desc))
    data = build_compare_data(
        tabs,
        settings.paths.runs_dir,
        settings.paths.cache_dir,
        args.limit,
        args.title,
        f"The same {args.limit} answers in every tab, from weak to strong by the teacher's mark.",
    )
    print(write_compare(data, settings.paths.runs_dir / args.out / "index.html"))


def _cmd_stress(args: argparse.Namespace, settings: Settings) -> None:
    items = select(
        load_dataset(args.dataset, settings.paths.data_dir), args.split, args.pool, args.seed
    )
    run_dir = settings.paths.runs_dir / args.name
    run_dir.mkdir(parents=True, exist_ok=True)
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
            settings.paths.cache_dir, grader, cfg.rubric_selftest, cfg.rubric_variant
        )
        questions = {c.item.question_key: to_question(c.item) for c in cases}
        with ThreadPoolExecutor(cfg.max_workers) as pool:
            records = dict(zip(questions, pool.map(store.get, questions.values()), strict=True))

        def mark(item):
            return mark_item(item, records[item.question_key], grader, cfg).grading.total

    rows = run_stress(cases, mark, settings.pipeline.max_workers)
    out = {"mode": args.mode, **summarise_stress(rows), "cost_usd": round(grader.usage.cost_usd, 3)}
    (run_dir / "stress.json").write_text(
        json.dumps({**out, "rows": rows}, indent=1), encoding="utf-8"
    )
    print(json.dumps(out, indent=2))


def _cmd_transfer(args: argparse.Namespace, settings: Settings) -> None:
    run_dir = settings.paths.runs_dir / args.name
    results = [r for r in read_results(run_dir / "results.jsonl") if r.feedback]
    if not results:
        sys.exit("No results with feedback in that run.")
    if args.sample:
        results = sample_by_mark(results, args.sample)
    grader, student = build_client(settings.llm), build_client(settings.student)
    rows = transfer_test(
        results, grader, student, grader, settings.paths.runs_dir, settings.pipeline.max_workers
    )
    out = {
        **summarise_transfer(rows),
        "cost_usd": round(grader.usage.cost_usd + student.usage.cost_usd, 3),
    }
    sfx = "_sample" if args.sample else ""
    (run_dir / f"transfer_rows{sfx}.jsonl").write_text(
        "\n".join(r.model_dump_json() for r in rows), encoding="utf-8"
    )
    (run_dir / f"transfer_scores{sfx}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


def _cmd_judge(args: argparse.Namespace, settings: Settings) -> None:
    run_dir = settings.paths.runs_dir / args.name
    results = [r for r in read_results(run_dir / "results.jsonl") if r.feedback]
    if not results:
        sys.exit("No results with feedback in that run.")
    grader = build_client(settings.llm)  # same cache path as the run, so schemes are reused
    store = RubricStore(
        settings.paths.cache_dir,
        grader,
        settings.pipeline.rubric_selftest,
        settings.pipeline.rubric_variant,
    )
    rubrics = {r.item.question_key: store.get(to_question(r.item)).rubric for r in results}
    judge_client = build_client(settings.judge)
    judgements = judge_all(results, rubrics, judge_client, settings.pipeline.max_workers)
    out = {"n": len(judgements), "pass_rates": pass_rates(judgements)}
    (run_dir / "feedback_judgements.jsonl").write_text(
        "\n".join(
            json.dumps({"id": r.item.id, **j.model_dump()})
            for r, j in zip(results, judgements, strict=True)
        ),
        encoding="utf-8",
    )
    (run_dir / "feedback_scores.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    print("report:", _write_view(run_dir, settings))


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = load_settings(args.config)
    if args.cmd == "download":
        download_all(settings.paths.data_dir)
        if args.engsaf:
            download_engsaf(settings.paths.data_dir)
    elif args.cmd == "run":
        _cmd_run(args, settings)
    elif args.cmd == "judge":
        _cmd_judge(args, settings)
    elif args.cmd == "report":
        results = read_results(settings.paths.runs_dir / args.name / "results.jsonl")
        print(json.dumps(report(results), indent=2))
    elif args.cmd == "compare":
        _cmd_compare(args, settings)
    elif args.cmd == "refeedback":
        _cmd_refeedback(args, settings)
    elif args.cmd == "sensitivity":
        runs = settings.paths.runs_dir
        a = read_results(runs / args.a / "results.jsonl")
        b = read_results(runs / args.b / "results.jsonl")
        print(json.dumps(compare_runs(a, b), indent=2))
    elif args.cmd == "stress":
        _cmd_stress(args, settings)
    elif args.cmd == "transfer":
        _cmd_transfer(args, settings)
    elif args.cmd == "votes":
        res = read_results(settings.paths.runs_dir / args.name / "results.jsonl")
        print(json.dumps({"voting": vote_report(res), "review": review_report(res)}, indent=2))
    elif args.cmd == "revision":
        _cmd_revision(args, settings)
    elif args.cmd == "rescore":
        _cmd_rescore(args, settings)
    elif args.cmd == "history":
        print(history())
    elif args.cmd == "log":
        print(record_run(settings.paths.runs_dir / args.name, args.variant, args.note))
    elif args.cmd == "view":
        print(_write_view(settings.paths.runs_dir / args.name, settings, args.limit, args.seed))


if __name__ == "__main__":
    main()

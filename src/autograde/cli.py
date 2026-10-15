"""Command line: download data, run the grader, judge feedback, print a report."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from autograde.config import Settings, load_settings
from autograde.datasets import LOADERS, load_dataset, select
from autograde.datasets.download import download_all
from autograde.evaluation.experiments import (
    comparisons,
    prompt_fingerprint,
    read_log,
    record_run,
)
from autograde.evaluation.judge import judge_all, pass_rates
from autograde.evaluation.metrics import report
from autograde.evaluation.revision import revision_test, summarise
from autograde.llm import build_client
from autograde.pipeline.feedback import write_feedback
from autograde.pipeline.rescore import rescore
from autograde.pipeline.rubric import RubricStore, cached_record
from autograde.pipeline.run import read_results, run_items, to_question
from autograde.vcs import GitError, commit_experiment, history
from autograde.viewer import sample_spread, write_report

log = logging.getLogger("autograde")


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="autograde", description=__doc__)
    p.add_argument("--config", type=Path, help="YAML settings (default: configs/default.yaml)")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("download", help="fetch the stage-1 datasets into data/raw")

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
    rf.add_argument("--feedback", choices=["standard", "hints", "critique"], required=True)
    rf.add_argument("--variant", required=True)
    rf.add_argument("--note", default="")
    rf.add_argument("--no-commit", action="store_true")

    rv = sub.add_parser("revision", help="test whether the feedback helps a student improve")
    rv.add_argument("--name", required=True)

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


def _write_view(run_dir: Path, settings: Settings, limit: int | None = None, seed: int = 0) -> Path:
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
        results = sample_spread(results, limit, seed)
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
    run_dir = settings.paths.runs_dir / args.name
    run_dir.mkdir(parents=True, exist_ok=True)
    client = build_client(settings.llm)
    setup = {
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


def _records(results: list, settings: Settings) -> dict:
    """Cached marking schemes for the questions in `results` (same cache path as the run)."""
    store = RubricStore(
        settings.paths.cache_dir,
        build_client(settings.llm),
        settings.pipeline.rubric_selftest,
        settings.pipeline.rubric_variant,
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
        fb = write_feedback(r.item, rubric, r.grading, client, args.feedback)
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
    grader, student = build_client(settings.llm), build_client(settings.student)
    rows = revision_test(
        results,
        _records(results, settings),
        grader,
        student,
        settings.pipeline,
        settings.paths.runs_dir / "revision_control.json",
        settings.pipeline.max_workers,
    )
    out = {
        **summarise(rows),
        "cost_usd": round(grader.usage.cost_usd + student.usage.cost_usd, 3),
    }
    (run_dir / "revision_rows.jsonl").write_text(
        "\n".join(r.model_dump_json() for r in rows), encoding="utf-8"
    )
    (run_dir / "revision_scores.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
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
    elif args.cmd == "run":
        _cmd_run(args, settings)
    elif args.cmd == "judge":
        _cmd_judge(args, settings)
    elif args.cmd == "report":
        results = read_results(settings.paths.runs_dir / args.name / "results.jsonl")
        print(json.dumps(report(results), indent=2))
    elif args.cmd == "refeedback":
        _cmd_refeedback(args, settings)
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

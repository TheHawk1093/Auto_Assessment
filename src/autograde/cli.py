"""Command line: download data, run the grader, judge feedback, print a report."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from autograde.config import Settings, load_settings
from autograde.datasets import LOADERS, load_dataset, select
from autograde.datasets.download import download_all
from autograde.evaluation.experiments import record_run
from autograde.evaluation.judge import judge_all, pass_rates
from autograde.evaluation.metrics import report
from autograde.llm import build_client
from autograde.pipeline.rubric import RubricStore
from autograde.pipeline.run import read_results, run_items, to_question
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

    judge = sub.add_parser("judge", help="score the feedback of a finished run")
    judge.add_argument("--name", required=True)

    rep = sub.add_parser("report", help="print metrics for a finished run")
    rep.add_argument("--name", required=True)

    logp = sub.add_parser("log", help="add a finished run to experiments/log.jsonl")
    logp.add_argument("--name", required=True)
    logp.add_argument("--variant", required=True)
    logp.add_argument("--note", default="")

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
    judged = {}
    jpath = run_dir / "feedback_judgements.jsonl"
    if jpath.exists():
        for line in jpath.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            judged[row.pop("id")] = row
    results = read_results(run_dir / "results.jsonl")
    if limit:
        results = sample_spread(results, limit, seed)
    return write_report(
        results,
        run_dir / ("report_sample.html" if limit else "report.html"),
        run_dir.name + (f" (sample of {len(results)})" if limit else ""),
        settings.paths.cache_dir,
        client_name,
        judged,
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
    summary = report(results)
    (run_dir / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (run_dir / "usage.json").write_text(json.dumps(client.usage.as_dict(), indent=2))
    print(json.dumps(summary, indent=2))
    print("usage:", client.usage.as_dict())
    print("report:", _write_view(run_dir, settings))
    print("logged:", record_run(run_dir, args.variant or args.mode, args.note))


def _cmd_judge(args: argparse.Namespace, settings: Settings) -> None:
    run_dir = settings.paths.runs_dir / args.name
    results = [r for r in read_results(run_dir / "results.jsonl") if r.feedback]
    if not results:
        sys.exit("No results with feedback in that run.")
    grader = build_client(settings.llm)  # same cache path as the run, so schemes are reused
    store = RubricStore(settings.paths.cache_dir, grader, settings.pipeline.rubric_selftest)
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
    elif args.cmd == "log":
        print(record_run(settings.paths.runs_dir / args.name, args.variant, args.note))
    elif args.cmd == "view":
        print(_write_view(settings.paths.runs_dir / args.name, settings, args.limit, args.seed))


if __name__ == "__main__":
    main()

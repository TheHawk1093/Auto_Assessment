"""Commands that grade answers or rework a finished run."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor

from autograde.cli.common import (
    finish,
    load_run,
    load_run_with_feedback,
    read_setup,
    run_client_name,
    run_dir,
    save_derived_run,
    write_json,
    write_lines,
    write_view,
)
from autograde.config import FEEDBACK_STYLES, Settings
from autograde.datasets import LOADERS, load_dataset, select
from autograde.datasets.download import download_all, download_engsaf
from autograde.datasets.perturb import perturb_items
from autograde.evaluation.experiments import record_run
from autograde.evaluation.judge import judge_all, pass_rates
from autograde.evaluation.metrics import report
from autograde.llm import build_client
from autograde.ocr.noise import noisy_items
from autograde.pipeline.feedback import write_feedback
from autograde.pipeline.rescore import rescore
from autograde.pipeline.rubric import RubricStore, cached_record
from autograde.pipeline.run import run_items, to_question
from autograde.vcs import history

log = logging.getLogger("autograde")
POC_ORDER = ("digiklausur", "saf", "mohler", "engsaf", "ricechem")  # simple to hard


def _add_commit_options(p: argparse.ArgumentParser, name_only: bool = False) -> None:
    p.add_argument("--variant", required=not name_only, help="label in the experiment log")
    p.add_argument("--note", default="", help="one line on what this variant changes")
    p.add_argument("--no-commit", action="store_true", help="skip the git commit and tag")


def register(sub) -> None:
    dl = sub.add_parser("download", help="fetch the stage-1 datasets into data/raw")
    dl.add_argument("--engsaf", action="store_true", help="also fetch EngSAF (benchmark only)")
    dl.set_defaults(func=cmd_download)

    run = sub.add_parser("run", help="grade a sample of answers")
    run.add_argument("--dataset", required=True, choices=sorted(LOADERS))
    run.add_argument("--split", default="dev", choices=["dev", "test"])
    run.add_argument("-n", type=int, default=20, help="sample size (omit for the whole split)")
    run.add_argument("--all", action="store_true", help="use the whole split")
    run.add_argument("--seed", type=int, default=0)
    run.add_argument("--mode", default="pipeline", choices=["pipeline", "baseline"])
    run.add_argument("--name", required=True, help="run folder name under runs/")
    run.add_argument(
        "--perturb-model", metavar="SPEC",
        help="alter model answers: mask<percent> blanks words, short<percent> keeps the start",
    )  # fmt: skip
    run.add_argument(
        "--ocr", choices=["light", "medium", "heavy"],
        help="add simulated OCR errors to the student answers",
    )  # fmt: skip
    _add_commit_options(run, name_only=True)
    run.set_defaults(func=cmd_run)

    poc = sub.add_parser("poc", help="small proof-of-concept run on each dataset, simple to hard")
    poc.add_argument("--datasets", default=",".join(POC_ORDER), help="comma separated")
    poc.add_argument("-n", type=int, default=8, help="answers per dataset")
    poc.add_argument("--seed", type=int, default=0)
    poc.add_argument("--baseline", action="store_true", help="also run the plain baseline")
    poc.add_argument("--no-commit", action="store_true")
    poc.set_defaults(func=cmd_poc)

    judge = sub.add_parser("judge", help="score the feedback of a finished run")
    judge.add_argument("--name", required=True)
    judge.set_defaults(func=cmd_judge)

    rep = sub.add_parser("report", help="print metrics for a finished run")
    rep.add_argument("--name", required=True)
    rep.set_defaults(func=cmd_report)

    rs = sub.add_parser(
        "rescore", help="re-price a finished run's verdicts with another partial weight (free)"
    )
    rs.add_argument("--name", required=True, help="source run")
    rs.add_argument("--new-name", required=True)
    rs.add_argument("--partial-weight", type=float, required=True)
    _add_commit_options(rs)
    rs.set_defaults(func=cmd_rescore)

    rf = sub.add_parser(
        "refeedback", help="rewrite the feedback of a finished run; marks stay the same"
    )
    rf.add_argument("--name", required=True, help="source run")
    rf.add_argument("--new-name", required=True)
    rf.add_argument("--feedback", choices=FEEDBACK_STYLES, required=True)
    rf.add_argument("--n", type=int, default=1, help="drafts to write; the best is kept")
    _add_commit_options(rf)
    rf.set_defaults(func=cmd_refeedback)

    lg = sub.add_parser("log", help="add a finished run to experiments/log.jsonl")
    lg.add_argument("--name", required=True)
    lg.add_argument("--variant", required=True)
    lg.add_argument("--note", default="")
    lg.set_defaults(func=cmd_log)

    sub.add_parser("history", help="list experiment tags with their scores").set_defaults(
        func=lambda args, settings: print(history())
    )

    view = sub.add_parser("view", help="(re)build runs/<name>/report.html to read the samples")
    view.add_argument("--name", required=True)
    view.add_argument("--limit", type=int, help="show only N answers, spread over questions")
    view.add_argument("--seed", type=int, default=0)
    view.set_defaults(func=cmd_view)


def cmd_download(args: argparse.Namespace, settings: Settings) -> None:
    download_all(settings.paths.data_dir)
    if args.engsaf:
        download_engsaf(settings.paths.data_dir)


def cmd_run(args: argparse.Namespace, settings: Settings) -> None:
    items = select(
        load_dataset(args.dataset, settings.paths.data_dir),
        args.split,
        None if args.all else args.n,
        args.seed,
    )
    if args.perturb_model:
        items = perturb_items(items, args.perturb_model, args.seed)
    if args.ocr:
        items = noisy_items(items, args.ocr, args.seed)
        settings.pipeline.ocr = args.ocr
    run = run_dir(settings, args.name)
    run.mkdir(parents=True, exist_ok=True)
    client = build_client(settings.llm)
    write_json(
        run / "run.json",
        {
            "perturb_model": args.perturb_model,
            "dataset": args.dataset,
            "split": args.split,
            "n": len(items),
            "seed": args.seed,
            "mode": args.mode,
            "variant": args.variant or args.mode,
            "llm": settings.llm.model_dump(),
            "pipeline": settings.pipeline.model_dump(),
        },
    )
    results = run_items(
        items,
        args.mode,
        client,
        settings,
        run / "results.jsonl",
        progress=lambda n, total: log.info("graded %d/%d", n, total),
    )
    finish(run, results, client.usage.as_dict(), settings, args)


def cmd_report(args: argparse.Namespace, settings: Settings) -> None:
    print(json.dumps(report(load_run(settings, args.name)), indent=2))


def cmd_log(args: argparse.Namespace, settings: Settings) -> None:
    print(record_run(run_dir(settings, args.name), args.variant, args.note))


def cmd_view(args: argparse.Namespace, settings: Settings) -> None:
    print(write_view(run_dir(settings, args.name), settings, args.limit, args.seed))


def cmd_rescore(args: argparse.Namespace, settings: Settings) -> None:
    src = run_dir(settings, args.name)
    setup = read_setup(src)
    if setup["mode"] != "pipeline":
        sys.exit("Only pipeline runs have verdicts to re-price.")
    model = run_client_name(setup, settings)
    variant = setup.get("pipeline", {}).get("rubric_variant", "generated")
    results = load_run(settings, args.name)
    rubrics = {}
    for r in results:
        rec = cached_record(settings.paths.rubrics_dir, model, r.item.question_key, variant)
        if rec is None:
            sys.exit(f"No stored marking scheme for {r.item.question_key}.")
        rubrics[r.item.question_key] = rec.rubric
    new = rescore(results, rubrics, args.partial_weight)
    changes = {
        "mark_rule": "status",
        "partial_weight": args.partial_weight,
        "rescored_from": args.name,
    }
    zero = {"calls": 0, "input_tokens": 0, "output_tokens": 0, "cost_usd": 0.0}
    save_derived_run(settings, args, new, setup, changes, zero)


def cmd_refeedback(args: argparse.Namespace, settings: Settings) -> None:
    results = load_run(settings, args.name)
    setup = read_setup(run_dir(settings, args.name))
    client = build_client(settings.llm)
    store = RubricStore(
        settings.paths.rubrics_dir,
        client,
        settings.pipeline.rubric_selftest,
        settings.pipeline.rubric_variant,
    )

    def redo(r):
        if r.grading is None:
            return r
        rubric = store.get(to_question(r.item)).rubric
        fb = write_feedback(r.item, rubric, r.grading, client, args.feedback, args.n)
        return r.model_copy(update={"feedback": fb})

    with ThreadPoolExecutor(settings.pipeline.max_workers) as pool:
        new = list(pool.map(redo, results))
    changes = {"feedback_variant": args.feedback, "refeedback_from": args.name}
    save_derived_run(settings, args, new, setup, changes, client.usage.as_dict())


def cmd_judge(args: argparse.Namespace, settings: Settings) -> None:
    run = run_dir(settings, args.name)
    results = load_run_with_feedback(settings, args.name)
    store = RubricStore(
        settings.paths.rubrics_dir,
        build_client(settings.llm),
        settings.pipeline.rubric_selftest,
        settings.pipeline.rubric_variant,
    )
    rubrics = {r.item.question_key: store.get(to_question(r.item)).rubric for r in results}
    judgements = judge_all(
        results, rubrics, build_client(settings.judge), settings.pipeline.max_workers
    )
    write_lines(
        run / "feedback_judgements.jsonl",
        [
            json.dumps({"id": r.item.id, **j.model_dump()})
            for r, j in zip(results, judgements, strict=True)
        ],
    )
    out = {"n": len(judgements), "pass_rates": pass_rates(judgements)}
    write_json(run / "feedback_scores.json", out)
    print(json.dumps(out, indent=2))
    print("report:", write_view(run, settings))


def cmd_poc(args: argparse.Namespace, settings: Settings) -> None:
    """A small run on each dataset in turn, pipeline and baseline, to see the shape of things."""
    for dataset in args.datasets.split(","):
        for mode in ("pipeline", "baseline"):
            if mode == "baseline" and not args.baseline:
                continue
            run_settings = settings.model_copy(deep=True)
            if dataset == "ricechem":
                run_settings.pipeline.rubric_variant = "official"
            cmd_run(
                argparse.Namespace(
                    dataset=dataset,
                    split="dev",
                    n=args.n,
                    all=False,
                    seed=args.seed,
                    mode=mode,
                    name=f"poc_{dataset}_{mode}",
                    variant=f"poc-{mode}",
                    note="proof of concept",
                    perturb_model=None,
                    ocr=None,
                    no_commit=args.no_commit,
                ),  # fmt: skip
                run_settings,
            )

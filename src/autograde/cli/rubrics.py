"""Commands that write, install and export marking schemes (rubrics)."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor

from autograde.cli.common import write_json
from autograde.config import Settings
from autograde.datasets import LOADERS, load_dataset
from autograde.datasets.ricechem import SPEC, official_record
from autograde.llm import build_client, client_name
from autograde.pipeline.levels import LEVELS
from autograde.pipeline.rubric import RubricStore, rubric_path
from autograde.pipeline.run import to_question
from autograde.viewer.rubrics_md import export_markdown


def register(sub) -> None:
    """Add the marking scheme commands to the subparsers."""
    rb = sub.add_parser("rubrics", help="write rubrics at each strictness level for a dataset")
    rb.add_argument("--dataset", required=True, choices=sorted(LOADERS))
    rb.add_argument("--levels", default=",".join(LEVELS), help="comma separated")
    rb.add_argument("--limit", type=int, help="only the first N questions (a trial)")
    rb.set_defaults(func=cmd_rubrics)

    og = sub.add_parser("official-rubrics", help="install the dataset's own rubrics (RiceChem)")
    og.set_defaults(func=cmd_official)

    md = sub.add_parser("rubrics-md", help="export stored rubrics as markdown files to read")
    md.add_argument("--dataset", required=True, choices=sorted(LOADERS))
    md.add_argument(
        "--variants",
        default=",".join(["generated", "sized", "official", *LEVELS]),
        help="comma separated",
    )
    md.set_defaults(func=cmd_markdown)


def cmd_rubrics(args: argparse.Namespace, settings: Settings) -> None:
    """Write marking schemes for a dataset at each strictness level."""
    questions = {}
    for item in load_dataset(args.dataset, settings.paths.data_dir):
        questions.setdefault(item.question_key, to_question(item))
    keys = sorted(questions)[: args.limit]
    client = build_client(settings.llm)
    for level in args.levels.split(","):
        store = RubricStore(settings.paths.rubrics_dir, client, run_selftest=False, variant=level)
        with ThreadPoolExecutor(settings.pipeline.max_workers) as pool:
            list(pool.map(store.get, [questions[k] for k in keys]))
        print(f"{args.dataset} {level}: {len(keys)} rubrics ready")
    print("cost so far:", round(client.usage.cost_usd, 2))


def cmd_official(args: argparse.Namespace, settings: Settings) -> None:
    """Store the official marking schemes as the `official` variant."""
    model = client_name(settings.llm)
    for qid in SPEC:
        record = official_record(qid)
        path = rubric_path(settings.paths.rubrics_dir, model, record.question_key, "official")
        path.parent.mkdir(parents=True, exist_ok=True)
        write_json(path, record.model_dump())
        print("wrote", path)


def cmd_markdown(args: argparse.Namespace, settings: Settings) -> None:
    """Export the stored marking schemes of a dataset as markdown."""
    model = client_name(settings.llm)
    for variant in args.variants.split(","):
        path = export_markdown(
            args.dataset, variant, model, settings.paths.data_dir, settings.paths.rubrics_dir
        )
        print(path or f"no {variant} rubrics stored for {args.dataset} under {model}")

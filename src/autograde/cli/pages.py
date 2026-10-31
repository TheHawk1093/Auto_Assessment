"""Commands that build the HTML pages for reading results."""

from __future__ import annotations

import argparse

from autograde.config import Settings
from autograde.llm import client_name
from autograde.viewer.compare import Tab, write_compare
from autograde.viewer.compare import build_data as build_compare_data
from autograde.viewer.rubrics import build_data as rubrics_data
from autograde.viewer.rubrics import write_page as write_rubrics
from autograde.viewer.styles import build_data as styles_data
from autograde.viewer.styles import write_page as write_styles

PAGE_DATASETS = ["digiklausur", "saf", "mohler", "engsaf"]


def register(sub) -> None:
    """Add the commands that build report pages to the subparsers."""
    sub.add_parser("styles-page", help="build output/runs/feedback_styles/index.html").set_defaults(
        func=cmd_styles
    )
    sub.add_parser("rubrics-page", help="build output/runs/rubrics/index.html").set_defaults(
        func=cmd_rubrics_page
    )
    cp = sub.add_parser("compare", help="one page, one tab per run, the same N answers in each")
    cp.add_argument(
        "--run", action="append", required=True, metavar="NAME=LABEL|SHORT|DESCRIPTION",
        help="repeat once per tab; the first run decides which answers are shown",
    )  # fmt: skip
    cp.add_argument("--limit", type=int, default=5)
    cp.add_argument("--title", default="Method comparison")
    cp.add_argument("--out", required=True, help="folder name under output/runs/")
    cp.set_defaults(func=cmd_compare)


def cmd_styles(args: argparse.Namespace, settings: Settings) -> None:
    """Build the feedback styles page."""
    data = styles_data(settings.paths.runs_dir)
    print(write_styles(data, settings.paths.runs_dir / "feedback_styles" / "index.html"))


def cmd_rubrics_page(args: argparse.Namespace, settings: Settings) -> None:
    """Build the page listing the stored marking schemes."""
    data = rubrics_data(
        settings.paths.data_dir,
        settings.paths.rubrics_dir,
        settings.paths.runs_dir,
        client_name(settings.llm),
        PAGE_DATASETS,
    )
    print(write_rubrics(data, settings.paths.runs_dir / "rubrics" / "index.html"))


def cmd_compare(args: argparse.Namespace, settings: Settings) -> None:
    """Build the page comparing several runs side by side."""
    tabs = []
    for spec in args.run:
        run, _, rest = spec.partition("=")
        label, _, rest = rest.partition("|")
        short, _, desc = rest.partition("|")
        tabs.append(Tab(run, label or run, short, desc))
    data = build_compare_data(
        tabs,
        settings.paths.runs_dir,
        settings.paths.rubrics_dir,
        args.limit,
        args.title,
        f"The same {args.limit} answers in every tab, from weak to strong by the teacher's mark.",
    )
    print(write_compare(data, settings.paths.runs_dir / args.out / "index.html"))

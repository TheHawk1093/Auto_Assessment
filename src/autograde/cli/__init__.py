"""Command line: download data, run the grader, test it, build the pages.

Each command module has a `register(sub)` that adds its subcommands and sets `func`.
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from autograde.cli import evals, pages, rubrics, runs
from autograde.config import load_settings

MODULES = (runs, evals, rubrics, pages)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="autograde", description=__doc__)
    p.add_argument("--config", type=Path, help="YAML settings (default: configs/default.yaml)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for module in MODULES:
        module.register(sub)
    return p


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args.func(args, load_settings(args.config))


if __name__ == "__main__":
    main()

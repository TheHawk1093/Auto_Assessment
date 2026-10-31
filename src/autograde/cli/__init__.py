"""Command line: download data, run the grader, test it, build the pages.

Each command module has a `register(sub)` that adds its subcommands and sets `func`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from autograde.cli import evals, exam, ocr, pages, recheck, rubrics, runs, scan
from autograde.config import load_settings
from autograde.logsetup import setup_logging

MODULES = (runs, evals, rubrics, pages, ocr, exam, scan, recheck)


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="autograde", description=__doc__)
    p.add_argument("--config", type=Path, help="YAML settings (default: configs/default.yaml)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for module in MODULES:
        module.register(sub)
    return p


def main(argv: list[str] | None = None) -> None:
    """Parse the command line, set up logging and run the chosen command.

    Args:
        argv: Arguments to parse; `sys.argv` when None.

    """
    args = _parser().parse_args(argv)
    settings = load_settings(args.config)
    setup_logging(settings.paths.logs_dir, args.cmd)
    args.func(args, settings)


if __name__ == "__main__":
    main()

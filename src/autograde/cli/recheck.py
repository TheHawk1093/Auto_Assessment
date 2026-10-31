"""Command that marks one answer of a finished exam again, with a note from the teacher.

It reuses the exam's stored marking scheme and the settings of its run, adds the teacher's note
for that question, and writes a proposal (mark, feedback) to a file. Nothing in the run changes:
the teacher decides whether the proposal replaces the mark.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autograde.cli.common import run_dir, write_json
from autograde.config import PipelineConfig, Settings
from autograde.intake.exam import student_of
from autograde.llm import build_client
from autograde.pipeline.run import read_results, run_items


def register(sub) -> None:
    """Add the `recheck` command and its flags to the subparsers."""
    p = sub.add_parser("recheck", help="mark one answer of a finished exam again, with a note")
    p.add_argument("--name", required=True, help="the exam's run name (runs/<name>/)")
    p.add_argument("--student", required=True)
    p.add_argument("--question", required=True)
    p.add_argument("--note", default="", help="what the teacher wants the marker to look at")
    p.add_argument("--out", type=Path, required=True, help="JSON file for the proposal")
    p.set_defaults(func=cmd_recheck)


def cmd_recheck(args: argparse.Namespace, settings: Settings) -> None:
    """Re-mark the one answer and write the proposal. Needs the original run's results."""
    out = run_dir(settings, args.name)
    run = json.loads((out / "run.json").read_text(encoding="utf-8"))
    settings.pipeline = PipelineConfig.model_validate(run["pipeline"])
    item = next(
        (
            r.item
            for r in read_results(out / "results.jsonl")
            if student_of(r.item) == args.student and r.item.question_id == args.question
        ),
        None,
    )
    if item is None:
        sys.exit(f"no marked answer for {args.student} question {args.question}")
    teacher = settings.pipeline.teacher
    note = "A recheck was asked for: look again at this answer with care. " + args.note.strip()
    before = teacher.question_notes.get(item.question_key, "")
    teacher.question_notes[item.question_key] = f"{before} {note}".strip()
    client = build_client(settings.llm)
    scratch = args.out.with_suffix(".results.jsonl")
    scratch.unlink(missing_ok=True)  # always a fresh marking, never a resumed one
    (result,) = run_items([item], "pipeline", client, settings, scratch)
    write_json(
        args.out,
        {
            "student": args.student,
            "question": args.question,
            "mark": result.predicted_mark,
            "max": item.max_mark,
            "feedback": result.feedback.text() if result.feedback else "",
            "flags": result.flags,
            "model": f"{settings.llm.backend}:{settings.llm.model}",
            "note": args.note,
        },
    )
    print(f"{args.student} Q{args.question}: {result.predicted_mark:g} / {item.max_mark:g}")

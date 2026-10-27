"""Command that marks a whole exam from its files: paper, reference files, student answers."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from autograde.cli.common import run_dir, write_json
from autograde.config import Settings, TeacherInputs
from autograde.intake.answers import load_answers
from autograde.intake.exam import (
    build_items,
    exam_key,
    marks_csv,
    schemes_markdown,
    student_markdown,
)
from autograde.intake.paper import load_paper
from autograde.intake.reference import load_references
from autograde.llm import build_client
from autograde.pipeline.rubric import store_for
from autograde.pipeline.run import run_items, to_question

log = logging.getLogger(__name__)


def register(sub) -> None:
    p = sub.add_parser("exam", help="mark an exam from its question paper, references and answers")
    p.add_argument(
        "--paper", type=Path, required=True, help="question paper (txt, md, docx, pdf, json)"
    )
    p.add_argument(
        "--reference", type=Path, nargs="*", default=[],
        help="model answer and/or rubric files, combined or separate (txt, md, docx, pdf, json)",
    )  # fmt: skip
    p.add_argument(
        "--answers", type=Path, required=True,
        help="folder with one file per student (or `autograde ocr` output), or one JSON file",
    )  # fmt: skip
    p.add_argument("--name", required=True, help="exam name; results go to runs/<name>/")
    p.add_argument(
        "--granularity", choices=["rubric", "none", "half", "quarter"], default="rubric",
        help="part marks: as the rubric says, none, halves, or quarters of a point",
    )  # fmt: skip
    p.add_argument("--strictness", choices=["lenient", "moderate", "strict"])
    p.add_argument("--note", default="", help="free text for the marker, e.g. 'units are required'")
    p.add_argument("--schemes-only", action="store_true", help="write the marking schemes and stop")
    p.set_defaults(func=cmd_exam)


def cmd_exam(args: argparse.Namespace, settings: Settings) -> None:
    client = build_client(settings.llm)
    out = run_dir(settings, args.name)
    out.mkdir(parents=True, exist_ok=True)

    paper = load_paper(args.paper, client)
    refs, warnings = load_references(args.reference, paper, client)
    answers, more = load_answers(args.answers, paper, client)
    warnings += more
    key = exam_key(args.name, paper, refs)
    write_json(
        out / "intake.json",
        {
            "paper": paper.model_dump(),
            "references": {k: v.model_dump() for k, v in refs.items()},
            "students": list(answers),
            "warnings": warnings,
        },
    )
    for w in warnings:
        print("warning:", w)
    print(f"{len(paper.questions)} questions, {paper.total:g} marks, {len(answers)} students")

    settings.pipeline.rubric_variant = "solid"
    settings.pipeline.with_feedback = True  # feedback is part of the product
    settings.pipeline.teacher = TeacherInputs(
        partial_credit=args.granularity, strictness=args.strictness, notes=args.note
    )
    items = build_items(key, paper, refs, answers)
    store = store_for(settings, grader=client)
    records: dict = {}
    first = {i.question_id: i for i in items}
    for q in paper.questions:  # one scheme per question, written once and cached
        item = first.get(q.id)
        if item is not None:
            records[q.id] = store.get(to_question(item))
    (out / "schemes.md").write_text(schemes_markdown(paper, records), encoding="utf-8")
    print("marking schemes:", out / "schemes.md")
    if args.schemes_only:
        return

    write_json(out / "run.json", {"mode": "pipeline", "pipeline": settings.pipeline.model_dump()})
    results = run_items(
        items,
        "pipeline",
        client,
        settings,
        out / "results.jsonl",
        progress=lambda n, total: log.info("marked %d/%d", n, total),
    )
    (out / "marks.csv").write_text(marks_csv(paper, results), encoding="utf-8")
    students = out / "students"
    students.mkdir(exist_ok=True)
    by_student: dict[str, list] = {}
    for r in results:
        by_student.setdefault(r.item.id.split("/")[1], []).append(r)
    for student, rs in by_student.items():
        (students / f"{student}.md").write_text(
            student_markdown(student, paper, rs), encoding="utf-8"
        )
    write_json(out / "usage.json", client.usage.as_dict())
    print(f"marks: {out / 'marks.csv'}   feedback: {students}")
    print(json.dumps(client.usage.as_dict()), file=sys.stderr)

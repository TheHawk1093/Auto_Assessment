"""Command that marks a whole exam from its files: paper, reference files, student answers."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from autograde.cli.common import run_dir, write_json
from autograde.config import Settings
from autograde.intake.answers import load_answers
from autograde.intake.exam import (
    build_items,
    exam_key,
    marks_csv,
    schemes_markdown,
    student_markdown,
)
from autograde.intake.models import ExamRules
from autograde.intake.paper import load_paper
from autograde.intake.reference import load_references
from autograde.intake.rules import apply_rules, extract_rules
from autograde.llm import build_client
from autograde.pipeline.rubric import rubric_client, store_for
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
        "--granularity", choices=["rubric", "stated", "none", "half", "quarter"],
        help="part marks, overriding what the rubric says: the rubric's own levels, only levels "
        "it names (else all or nothing), none, halves, or quarters of a point",
    )  # fmt: skip
    p.add_argument(
        "--mark-step", type=float,
        help="marks come in multiples of this: 0.5 allows 1.5 out of 2, 0.2 allows 1.8",
    )  # fmt: skip
    p.add_argument("--strictness", choices=["lenient", "moderate", "strict"])
    p.add_argument("--note", default="", help="free text for the marker, e.g. 'units are required'")
    p.add_argument(
        "--question-note", action="append", default=[], metavar="ID=TEXT",
        help="a note for one question only (repeat for more), e.g. 2b='accept either method'",
    )  # fmt: skip
    p.add_argument(
        "--max-mark", type=float,
        help="marks for a single question whose paper does not print them",
    )  # fmt: skip
    p.add_argument(
        "--no-follow-through", action="store_true",
        help="do not credit a later part that is right on the student's own earlier result",
    )  # fmt: skip
    p.add_argument(
        "--working-required", action="store_true",
        help="a numerical answer with no formula or working written earns no marks",
    )  # fmt: skip
    p.add_argument(
        "--ignore-rubric-rules", action="store_true",
        help="do not read exam-wide marking rules (whole marks, working required, carry-through) "
        "from the paper and rubric",
    )  # fmt: skip
    p.add_argument(
        "--code-exec", action="store_true",
        help="run tests on student code in the sandbox (the model writes tests if none are given)",
    )  # fmt: skip
    p.add_argument(
        "--code-sandbox", choices=["wasm", "docker", "process"], default="wasm",
        help="where code runs: wasm (default, stdlib only), docker, or process (trusted code only)",
    )  # fmt: skip
    p.add_argument("--schemes-only", action="store_true", help="write the marking schemes and stop")
    p.set_defaults(func=cmd_exam)


def rules_markdown(rules: ExamRules) -> str:
    """The exam-wide rules read from the documents, shown above the schemes for the teacher."""
    if not rules.found:
        return ""
    lines = ["## Exam-wide rules read from the paper and rubric", ""]
    if rules.working_required:
        lines.append("- A numerical answer with no formula or working earns no marks.")
    if rules.part_marks != "unstated":
        lines.append(f"- Part marks: {rules.part_marks.replace('_', ' ')}.")
    if rules.mark_step:
        lines.append(f"- Marks come in multiples of {rules.mark_step:g}.")
    if rules.follow_through is not None:
        lines.append(
            f"- Follow-through on earlier parts: {'yes' if rules.follow_through else 'no'}."
        )
    lines += [f"- {n}" for n in rules.notes]
    return "\n".join(lines) + "\n\n"


def cmd_exam(args: argparse.Namespace, settings: Settings) -> None:
    client = build_client(settings.llm)
    out = run_dir(settings, args.name)
    out.mkdir(parents=True, exist_ok=True)

    paper = load_paper(args.paper, client, args.max_mark)
    refs, warnings = load_references(args.reference, paper, client)
    answers, more = load_answers(args.answers, paper, client)
    warnings += more
    key = exam_key(args.name, paper, refs)
    rules = ExamRules()
    if not args.ignore_rubric_rules:
        rules = extract_rules(
            args.paper, args.reference, rubric_client(settings, settings.pipeline)
        )
    write_json(
        out / "intake.json",
        {
            "paper": paper.model_dump(),
            "references": {k: v.model_dump() for k, v in refs.items()},
            "rules": rules.model_dump(),
            "students": list(answers),
            "warnings": warnings,
        },
    )
    for w in warnings:
        print("warning:", w)
    print(f"{len(paper.questions)} questions, {paper.total:g} marks, {len(answers)} students")

    settings.pipeline.rubric_variant = "solid"
    settings.pipeline.with_feedback = True  # feedback is part of the product
    notes = dict(n.split("=", 1) for n in args.question_note if "=" in n)
    settings.pipeline.teacher = apply_rules(
        rules,
        granularity=args.granularity,
        mark_step=args.mark_step,
        strictness=args.strictness,
        follow_through=False if args.no_follow_through else None,
        working_required=args.working_required,
        notes=args.note,
        question_notes={f"{key}/{qid.strip()}": text for qid, text in notes.items()},
    )
    if rules.found:
        print("rules read from the paper and rubric:", rules.model_dump_json())
    settings.pipeline.code_exec = args.code_exec
    settings.pipeline.code_sandbox = args.code_sandbox
    items = build_items(key, paper, refs, answers)
    store = store_for(settings, grader=client)
    records: dict = {}
    first = {i.question_id: i for i in items}
    for q in paper.questions:  # one scheme per question, written once and cached
        item = first.get(q.id)
        if item is not None:
            records[q.id] = store.get(to_question(item))
    header = rules_markdown(rules)
    (out / "schemes.md").write_text(header + schemes_markdown(paper, records), encoding="utf-8")
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

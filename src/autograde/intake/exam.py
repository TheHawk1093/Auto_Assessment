"""Put the parts of an exam together as grader items, and write what the teacher reads."""

from __future__ import annotations

import hashlib
import re

from autograde.intake.answers import Answers
from autograde.intake.models import Paper, Reference
from autograde.schemas import Item, Result, RubricRecord


def exam_key(name: str, paper: Paper, refs: dict[str, Reference]) -> str:
    """The dataset name of an exam. It changes when the paper or the references change, so a
    stored marking scheme is never reused for a question that was edited."""
    digest = hashlib.sha1(
        (
            paper.model_dump_json() + str(sorted((k, v.model_dump_json()) for k, v in refs.items()))
        ).encode()
    ).hexdigest()[:8]
    return f"{re.sub(r'[^A-Za-z0-9_-]+', '-', name)}.{digest}"


def build_items(key: str, paper: Paper, refs: dict[str, Reference], answers: Answers) -> list[Item]:
    """One item per student per question. Missing answers become empty strings (marked zero)."""
    items = []
    for student, per_q in answers.items():
        slug = re.sub(r"[^A-Za-z0-9_-]+", "-", student).strip("-") or "student"
        for q in paper.questions:
            ref = refs.get(q.id, Reference())
            items.append(
                Item(
                    id=f"{key}/{slug}/{q.id}",
                    dataset=key,
                    question_id=q.id,
                    question=q.text,
                    model_answer=ref.model_answer,
                    rubric=ref.rubric,
                    student_answer=per_q.get(q.id, ""),
                    max_mark=q.max_mark,
                    kind=q.kind,
                    field=q.field,
                )
            )
    return items


def student_of(item: Item) -> str:
    return item.id.split("/")[1]


def schemes_markdown(paper: Paper, records: dict[str, RubricRecord]) -> str:
    """The marking schemes for the teacher to read before the exam is marked."""
    out = [f"# Marking schemes: {paper.title or 'exam'} ({paper.total:g} marks)\n"]
    for q in paper.questions:
        rec = records.get(q.id)
        out.append(f"## Question {q.id} ({q.max_mark:g} marks, {q.kind})\n\n{q.text}\n")
        if rec is None:
            continue
        r = rec.rubric
        out.append("```\n" + r.render() + "\n```\n")
        if r.answer_key:
            out.append(f"Answer key worked out: {r.answer_key}\n")
        if rec.review_notes:
            out.append("Review found: " + " | ".join(rec.review_notes) + "\n")
        if rec.selftest_passed is False:
            out.append("**Self-test failed:** " + " | ".join(rec.selftest_notes) + "\n")
    return "\n".join(out)


def student_markdown(student: str, paper: Paper, results: list[Result]) -> str:
    """One student's marks and feedback, question by question."""
    by_q = {r.item.question_id: r for r in results}
    got = sum(r.predicted_mark for r in by_q.values())
    out = [f"# {student}: {got:g} / {paper.total:g}\n"]
    for q in paper.questions:
        r = by_q.get(q.id)
        if r is None:
            continue
        out.append(f"## Question {q.id}: {r.predicted_mark:g} / {q.max_mark:g}\n")
        if r.feedback:
            out.append(r.feedback.text() + "\n")
        if r.flags:
            out.append(f"_For the teacher: {', '.join(r.flags)}_\n")
    return "\n".join(out)


def marks_csv(paper: Paper, results: list[Result]) -> str:
    rows = [",".join(["student", *paper.ids, "total"])]
    students: dict[str, dict[str, float]] = {}
    for r in results:
        students.setdefault(student_of(r.item), {})[r.item.question_id] = r.predicted_mark
    for student, per_q in sorted(students.items()):
        cells = [f"{per_q[i]:g}" if i in per_q else "" for i in paper.ids]
        rows.append(",".join([student, *cells, f"{sum(per_q.values()):g}"]))
    return "\n".join(rows) + "\n"

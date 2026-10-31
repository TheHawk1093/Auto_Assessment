"""Put the parts of an exam together as grader items, and write what the teacher reads."""

from __future__ import annotations

import hashlib
import re

from autograde.intake.answers import Answers
from autograde.intake.counting import Counting, counted_total, group_of
from autograde.intake.figures import split_figures
from autograde.intake.models import Paper, Reference
from autograde.schemas import Item, Result, RubricRecord


def exam_key(name: str, paper: Paper, refs: dict[str, Reference]) -> str:
    """Return the dataset name of an exam.

    It changes when the paper or the references change, so a stored marking scheme is never
    reused for a question that was edited.
    """
    digest = hashlib.sha1(
        (
            paper.model_dump_json() + str(sorted((k, v.model_dump_json()) for k, v in refs.items()))
        ).encode()
    ).hexdigest()[:8]
    return f"{re.sub(r'[^A-Za-z0-9_-]+', '-', name)}.{digest}"


PART = re.compile(r"^q?(\d+)\W*([a-z])", re.IGNORECASE)
EARLIER_LIMIT = 600  # characters of each earlier answer shown to the marker


def question_number(question_id: str) -> str | None:
    """Return the leading number when the id is a part of a numbered question.

    2b gives 2; 3 gives None (a whole question, not a part).
    """
    match = PART.match(question_id.strip())
    return match.group(1) if match else None


def earlier_parts(paper: Paper, position: int, per_q: dict[str, str]) -> str:
    """Return the student's answers to the earlier parts of the same numbered question.

    A part that builds on them can then be marked on the student's own result.
    """
    number = question_number(paper.questions[position].id)
    if number is None:
        return ""
    lines = []
    for before in paper.questions[:position]:
        if question_number(before.id) == number:
            text = per_q.get(before.id, "").strip()[:EARLIER_LIMIT] or "(no answer)"
            lines.append(f"Part {before.id}: {text}")
    return "\n".join(lines)


def build_items(key: str, paper: Paper, refs: dict[str, Reference], answers: Answers) -> list[Item]:
    """Build one item per student per question.

    Missing answers become empty strings (marked zero). A later part of a multi-part question
    carries the student's answers to its earlier parts.
    """
    items = []
    for student, per_q in answers.items():
        slug = re.sub(r"[^A-Za-z0-9_-]+", "-", student).strip("-") or "student"
        for position, q in enumerate(paper.questions):
            ref = refs.get(q.id, Reference())
            words, drawn = split_figures(per_q.get(q.id, ""))
            model_words, model_figs = split_figures(ref.model_answer)
            if drawn and not words:
                words = "(the answer is a drawing)"
            items.append(
                Item(
                    id=f"{key}/{slug}/{q.id}",
                    dataset=key,
                    question_id=q.id,
                    question=q.text,
                    model_answer=model_words,
                    rubric=ref.rubric,
                    tests=ref.tests,
                    student_answer=words,
                    figures=drawn,
                    reference_figure=model_figs[0] if model_figs else "",
                    max_mark=q.max_mark,
                    kind="diagram" if drawn and q.kind == "short" else q.kind,
                    field=q.field,
                    earlier=earlier_parts(paper, position, per_q),
                )
            )
    return items


def student_of(item: Item) -> str:
    """Return the student part of an item id."""
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


def _first_part(paper: Paper, group: str) -> str:
    return next(q.id for q in paper.questions if group_of(q.id) == group)


def student_markdown(
    student: str, paper: Paper, results: list[Result], counting: Counting | None = None
) -> str:
    """One student's marks and feedback, question by question."""
    counting = counting or Counting()
    by_q = {r.item.question_id: r for r in results}
    marks = {i: r.predicted_mark for i, r in by_q.items()}
    counted = counted_total(marks, paper, student, counting) if counting.active else None
    if counted:
        out = [f"# {student}: {counted.total:g} / {counted.out_of:g}\n"]
        out.append(f"Counted questions: {', '.join(counted.groups)}.\n")
    else:
        out = [f"# {student}: {sum(marks.values()):g} / {paper.total:g}\n"]
    for q in paper.questions:
        r = by_q.get(q.id)
        group = group_of(q.id)
        if r is None:
            if counting.is_struck(student, q.id) and q.id == _first_part(paper, group):
                out.append(f"## Question {group}: struck out by the student, not marked\n")
            continue
        note = " (not counted)" if counted and group not in counted.groups else ""
        out.append(f"## Question {q.id}: {r.predicted_mark:g} / {q.max_mark:g}{note}\n")
        if r.feedback:
            out.append(r.feedback.text() + "\n")
        if r.flags:
            out.append(f"_For the teacher: {', '.join(r.flags)}_\n")
    return "\n".join(out)


def marks_csv(paper: Paper, results: list[Result], counting: Counting | None = None) -> str:
    """Build the marks table as CSV: one row per student, one column per question."""
    counting = counting or Counting()
    extra = ["counted_total", "counted_out_of", "counted_questions"] if counting.active else []
    rows = [",".join(["student", *paper.ids, "total", *extra])]
    students: dict[str, dict[str, float]] = {}
    for r in results:
        students.setdefault(student_of(r.item), {})[r.item.question_id] = r.predicted_mark
    for student, per_q in sorted(students.items()):
        cells = [f"{per_q[i]:g}" if i in per_q else "" for i in paper.ids]
        tail = []
        if counting.active:
            c = counted_total(per_q, paper, student, counting)
            tail = [f"{c.total:g}", f"{c.out_of:g}", "+".join(c.groups)]
        rows.append(",".join([student, *cells, f"{sum(per_q.values()):g}", *tail]))
    return "\n".join(rows) + "\n"

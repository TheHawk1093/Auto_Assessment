"""The marks a student actually gets: the model's mark, or the teacher's override of it.

Everything that shows or exports marks (teacher tables, downloads, the student's page) goes
through here, so an override changes all of them at once. Totals follow the best-of-n rule
(`intake/counting.py`), the same one the command line applies.
"""

from __future__ import annotations

import pandas as pd

from app.services import db, notifications, results, storage, students
from autograde.intake.counting import Counting, counted_total, parse_struck
from autograde.intake.models import Paper


def paper(exam_id: str) -> Paper:
    """Load the exam's paper (questions and marks) from its intake."""
    return Paper.model_validate(results.intake(exam_id)["paper"])


def counting(exam_id: str) -> Counting:
    """Best-of-n and struck-out questions: the teacher's settings win over the paper's rules."""
    settings = storage.load_meta(exam_id)["settings"]
    rules = results.intake(exam_id).get("rules", {})
    return Counting(
        settings["count_best"] or rules.get("count_best"), parse_struck(settings["struck_out"])
    )


def overrides(exam_id: str) -> dict[tuple[str, str], dict]:
    """Return the teacher's mark overrides as {(student, question): row}."""
    with db.connect() as c:
        rows = c.execute("SELECT * FROM overrides WHERE exam_id = ?", (exam_id,)).fetchall()
    return {(r["student"], r["question"]): dict(r) for r in rows}


def final_marks(exam_id: str) -> dict[str, dict[str, float]]:
    """{student: {question id: mark}} with overrides applied."""
    over = overrides(exam_id)
    out: dict[str, dict[str, float]] = {}
    for r in results.results(exam_id):
        student, qid = results.student_of(r.item), r.item.question_id
        mark = over[(student, qid)]["mark"] if (student, qid) in over else r.predicted_mark
        out.setdefault(student, {})[qid] = mark
    return out


def student_total(exam_id: str, student: str, marks: dict[str, float]) -> tuple[float, float]:
    """(total, out of) for one student, honouring best-of-n."""
    p, count = paper(exam_id), counting(exam_id)
    if count.active:
        c = counted_total(marks, p, student, count)
        return c.total, c.out_of
    return round(sum(marks.values()), 6), p.total


def marks_table(exam_id: str) -> pd.DataFrame:
    """One row per student: each question, the total, and the counted total when best-of-n is on."""
    p, count = paper(exam_id), counting(exam_id)
    rows = []
    for student, marks in sorted(final_marks(exam_id).items()):
        row = {"student": student, **{q: marks.get(q) for q in p.ids}, "total": sum(marks.values())}
        if count.active:
            c = counted_total(marks, p, student, count)
            row |= {
                "counted_total": c.total,
                "counted_out_of": c.out_of,
                "counted_questions": "+".join(c.groups),
            }
        rows.append(row)
    return pd.DataFrame(rows)


def override(
    exam_id: str, student: str, question: str, mark: float, comment: str, by: str,
    notify: bool = True,
) -> None:  # fmt: skip
    """Set the teacher's mark for one answer. Must lie between 0 and the question's marks.

    Once the results are published the student is told, unless the caller says something to them
    itself (a regrade decision does).
    """
    spec = next((q for q in paper(exam_id).questions if q.id == question), None)
    if spec is None:
        raise ValueError(f"No question {question!r} in this exam.")
    if not 0 <= mark <= spec.max_mark:
        raise ValueError(f"The mark must be between 0 and {spec.max_mark:g}.")
    with db.connect() as c:
        c.execute(
            "INSERT OR REPLACE INTO overrides"
            " (exam_id, student, question, mark, comment, by_user, at)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (exam_id, student, question, mark, comment.strip(), by, db.now()),
        )
    db.audit(by, "override", f"{exam_id} {student} Q{question} -> {mark:g}")
    meta = storage.load_meta(exam_id)
    if notify and meta["published"]:
        notifications.notify(
            students.account_of(student), "mark_changed",
            f"Your mark for question {question} in {meta['title']} was changed.", exam_id,
        )  # fmt: skip


def clear_override(exam_id: str, student: str, question: str, by: str) -> None:
    """Remove the teacher's override so the model's mark stands again."""
    with db.connect() as c:
        c.execute(
            "DELETE FROM overrides WHERE exam_id = ? AND student = ? AND question = ?",
            (exam_id, student, question),
        )
    db.audit(by, "clear_override", f"{exam_id} {student} Q{question}")

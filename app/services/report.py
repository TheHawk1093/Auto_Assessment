"""One student's marked exam as plain data, with overrides applied.

The teacher's exports and the student's page both read this, so they can never disagree. It
does no permission checks; `publishing.student_view` adds those for students.
"""

from __future__ import annotations

from app.services import grades, results


def rows(exam_id: str, student: str) -> list[dict]:
    """One dict per marked question, in paper order."""
    over = grades.overrides(exam_id)
    by_q = {
        r.item.question_id: r
        for r in results.results(exam_id)
        if results.student_of(r.item) == student
    }
    out = []
    for q in grades.paper(exam_id).questions:
        r = by_q.get(q.id)
        if r is None:  # struck out by the student, or never marked
            continue
        o = over.get((student, q.id))
        out.append(
            {
                "question": q.id,
                "text": q.text,
                "max": q.max_mark,
                "model_mark": r.predicted_mark,
                "mark": o["mark"] if o else r.predicted_mark,
                "overridden": o is not None,
                "teacher_comment": o["comment"] if o else "",
                "feedback": r.feedback.text() if r.feedback else "",
                "answer": r.item.student_answer,
                "reference": r.item.model_answer,
            }
        )
    return out


def markdown(exam_id: str, student: str) -> str:
    """The student's marks and feedback as one document (final marks)."""
    rs = rows(exam_id, student)
    marks = {r["question"]: r["mark"] for r in rs}
    total, out_of = grades.student_total(exam_id, student, marks)
    lines = [f"# {student}: {total:g} / {out_of:g}\n"]
    for r in rs:
        lines.append(f"## Question {r['question']}: {r['mark']:g} / {r['max']:g}\n")
        if r["feedback"]:
            lines.append(r["feedback"] + "\n")
        if r["overridden"]:
            note = f" {r['teacher_comment']}" if r["teacher_comment"] else ""
            lines.append(f"_Mark changed by the teacher (was {r['model_mark']:g}).{note}_\n")
    return "\n".join(lines)

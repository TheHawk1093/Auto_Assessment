"""What the teacher downloads. All built from final marks (overrides applied)."""

from __future__ import annotations

import io
import zipfile

import pandas as pd

from app.services import grades, report, results
from autograde.pipeline.review import LABELS, review_reasons


def marks_csv(exam_id: str) -> bytes:
    """Return the final marks as CSV bytes that Excel opens correctly."""
    return (
        grades.marks_table(exam_id).to_csv(index=False).encode("utf-8-sig")
    )  # Excel opens it right


def excel_bytes(exam_id: str) -> bytes:
    """Marks sheet, then one row per answer with the mark, feedback and why it may need a look."""
    over = grades.overrides(exam_id)
    detail = []
    for r in results.results(exam_id):
        student, qid = results.student_of(r.item), r.item.question_id
        o = over.get((student, qid))
        detail.append(
            {
                "student": student,
                "question": qid,
                "mark": o["mark"] if o else r.predicted_mark,
                "model mark": r.predicted_mark,
                "out of": r.item.max_mark,
                "teacher comment": o["comment"] if o else "",
                "feedback": r.feedback.text() if r.feedback else "",
                "flags": ", ".join(r.flags),
                "to check": "; ".join(LABELS[x] for x in review_reasons(r)),
            }
        )
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xl:
        grades.marks_table(exam_id).to_excel(xl, sheet_name="Marks", index=False)
        pd.DataFrame(detail).to_excel(xl, sheet_name="Feedback", index=False)
    return buf.getvalue()


def feedback_zip(exam_id: str) -> bytes:
    """Return a zip with one markdown feedback report per student."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for student in sorted(grades.final_marks(exam_id)):
            z.writestr(f"{student}.md", report.markdown(exam_id, student))
    return buf.getvalue()

"""The publish gate.

A student can read an exam only when all three hold: the teacher has published it, the student
has marks in it, and (for an exam that belongs to a course) the student is enrolled in that
course. Every student-facing read goes through `can_view` and `student_view`; there is no
other path.
"""

from __future__ import annotations

from app.services import courses, db, grades, notifications, report, results, storage
from app.text import normalize


def publish(exam_id: str, by: str) -> None:
    """Publish the exam's results to students.

    Raises:
        ValueError: If the exam has not been marked.
    """
    if not results.has_results(exam_id):
        raise ValueError("Mark the exam before publishing it.")
    meta = storage.load_meta(exam_id)
    already = bool(meta["published"])
    storage.set_published(exam_id, True)
    db.audit(by, "publish", exam_id)
    if not already:
        meta = storage.load_meta(exam_id)
        notifications.notify_students(
            [s for s in sorted(marked_students(exam_id)) if can_view(exam_id, s, meta)],
            "published",
            f"Results are out for {meta['title']}.",
            exam_id,
        )


def unpublish(exam_id: str, by: str) -> None:
    """Take the results back from students.

    Raises:
        ValueError: If students have already asked for regrades.
    """
    with db.connect() as c:
        asked = c.execute("SELECT 1 FROM regrades WHERE exam_id = ? LIMIT 1", (exam_id,)).fetchone()
    if asked:
        raise ValueError(
            "Students have already asked for regrades, so this can no longer be undone."
        )
    storage.set_published(exam_id, False)
    db.audit(by, "unpublish", exam_id)


def marked_students(exam_id: str) -> set[str]:
    """Return the (normalised) ids of students who have marks in the exam."""
    return {normalize(s) for s in results.intake(exam_id).get("students", [])}


def can_view(exam_id: str, student_id: str, meta: dict | None = None) -> bool:
    """May this student see this exam's results? Published, marked, and enrolled in its course."""
    meta = meta or storage.load_meta(exam_id)
    if not meta["published"] or normalize(student_id) not in marked_students(exam_id):
        return False
    course_id = meta["course_id"]
    return course_id is None or courses.is_enrolled(course_id, student_id)


def exams_for_student(student_id: str) -> list[dict]:
    """Published exams this student may see, newest first."""
    return [m for m in storage.list_exams() if can_view(m["id"], student_id, m)]


def student_view(exam_id: str, student_id: str) -> dict:
    """Return the student's own results, shaped by the teacher's policy.

    Raises:
        PermissionError: If the student may not see this exam.
    """
    meta = storage.load_meta(exam_id)
    if not can_view(exam_id, student_id, meta):
        raise PermissionError("These results are not available.")
    policy = meta["policy"]
    rows = []
    for r in report.rows(exam_id, student_id):
        rows.append(
            {
                "question": r["question"],
                "text": r["text"],
                "max": r["max"],
                "mark": r["mark"],
                "feedback": r["feedback"],
                "teacher_comment": r["teacher_comment"],
                "mark_changed": r["overridden"],
                "answer": r["answer"] if policy["show_answer"] else "",
                "reference": r["reference"] if policy["show_reference"] else "",
            }
        )
    total, out_of = grades.student_total(
        exam_id, student_id, {r["question"]: r["mark"] for r in rows}
    )
    return {
        "exam": meta["title"],
        "published": meta["published"],
        "total": total,
        "out_of": out_of,
        "rows": rows,
        "policy": policy,
    }


def roster_problems(exam_id: str) -> dict[str, list[str]]:
    """Find mismatches between who was marked and who is enrolled.

    `not_enrolled` have marks but no active enrolment (they cannot see the results); `no_marks`
    are enrolled but have no marked answers (absent, or the file name did not match).
    """
    course_id = storage.load_meta(exam_id)["course_id"]
    if course_id is None:
        return {"not_enrolled": [], "no_marks": []}
    marked = marked_students(exam_id)
    enrolled = {normalize(r["student_id"]) for r in courses.roster(course_id)}
    return {"not_enrolled": sorted(marked - enrolled), "no_marks": sorted(enrolled - marked)}

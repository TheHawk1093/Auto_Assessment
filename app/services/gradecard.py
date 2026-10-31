"""A student's grade card: every course they are enrolled in, and in each the published exams.

It is computed from the live marks every time (the model's marks with the teacher's overrides),
so an upheld regrade, a changed mark, a new enrolment or a drop shows up the next time it is read.
Nothing here is stored. Visibility goes through `publishing.can_view`, the same gate as the exam
page, so the card can never show a student something the exam page would refuse.

A course's percentage is its marks over what its published exams were worth. The overall figure is
the mean of the course percentages, so a course with many small tests does not drown out one with a
single large exam.
"""

from __future__ import annotations

from app.services import courses, grades, publishing, regrades, storage


def _exam_line(meta: dict, student_id: str) -> dict:
    marks = grades.final_marks(meta["id"]).get(student_id, {})
    total, out_of = grades.student_total(meta["id"], student_id, marks)
    return {
        "exam_id": meta["id"],
        "title": meta["title"],
        "published": meta["published"],
        "total": total,
        "out_of": out_of,
        "percent": round(100 * total / out_of, 1) if out_of else 0.0,
        "pending_regrades": sum(
            r["status"] == "pending" for r in regrades.list_requests(meta["id"], student_id)
        ),
    }


def for_student(student_id: str) -> dict:
    """{student_id, courses: [{course, exams, total, out_of, percent}], overall_percent}."""
    cards = []
    for course in courses.courses_of(student_id):
        exams = [
            _exam_line(m, student_id)
            for m in storage.list_exams()
            if m["course_id"] == course["id"] and publishing.can_view(m["id"], student_id, m)
        ]
        total = round(sum(e["total"] for e in exams), 6)
        out_of = round(sum(e["out_of"] for e in exams), 6)
        cards.append(
            {
                "course": course,
                "exams": sorted(exams, key=lambda e: e["published"]),
                "total": total,
                "out_of": out_of,
                "percent": round(100 * total / out_of, 1) if out_of else None,
            }
        )
    marked = [c["percent"] for c in cards if c["percent"] is not None]
    return {
        "student_id": student_id,
        "courses": cards,
        "overall_percent": round(sum(marked) / len(marked), 1) if marked else None,
    }

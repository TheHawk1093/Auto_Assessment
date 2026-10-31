"""One line of facts per exam, for the teacher's overview and the admin's table."""

from __future__ import annotations

from app.services import courses, models, regrades, results, storage


def summary(meta: dict) -> dict:
    """What an exam card shows. Reads only small files (never the results)."""
    exam_id = meta["id"]
    info = results.intake(exam_id)
    return {
        "id": exam_id,
        "title": meta["title"],
        "owner": meta["owner"],
        "created": meta["created"],
        "status": storage.exam_status(exam_id),
        "model": models.get(meta["model"]).label,
        "course": courses.label(courses.get(meta["course_id"])),
        "students": len(info.get("students", [])),
        "questions": len(info.get("paper", {}).get("questions", [])),
        "pending": regrades.pending_count(exam_id),
    }


def for_owner(owner: str | None) -> list[dict]:
    """Summaries of one teacher's exams, or of all exams when `owner` is None."""
    return [summary(m) for m in storage.list_exams(owner)]

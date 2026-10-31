"""Who wrote which sheet: the pipeline's report, and the teacher's corrections to it.

The pipeline (`autograde exam --directory ...`) reads the roll number and name written on each
sheet, checks them against the student database and writes `identity.json`: one entry per sheet
with who it decided on, how, and what to look at. Whatever it could not settle is shown to the
teacher, who picks the student; that choice is saved in `identity_fixes.json` and given back to the
pipeline on the next run, so a fix survives re-marking.
"""

from __future__ import annotations

import json

from app.services import courses, roster, storage, students
from app.services.storage import exam_dir, run_path


def report(exam_id: str) -> list[dict]:
    """Return one entry per sheet from the last run, with the teacher's fixes applied.

    A fixed sheet reads as resolved by the teacher.
    """
    path = run_path(exam_id) / "identity.json"
    entries = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    fixes = fixes_for(exam_id)
    for e in entries:
        fixed = fixes.get(e["source"])
        if fixed:
            e.update(student_id=fixed, name=name_of(exam_id, fixed), method="teacher", status="ok")
            e["flags"] = []
    return entries


def blocking(exam_id: str) -> list[dict]:
    """Sheets that still cannot be attributed to a student."""
    return [e for e in report(exam_id) if e["status"] == "unresolved"]


def needs_check(exam_id: str) -> list[dict]:
    """Sheets matched but worth a person's check."""
    return [e for e in report(exam_id) if e["status"] == "check"]


def roster_people(exam_id: str) -> dict[str, dict]:
    """Students named in the roster uploaded with this exam, who may not be in the database yet."""
    path = roster.roster_file(exam_id)
    return roster.parse_roster(path.read_bytes()) if path else {}


def name_of(exam_id: str, student_id: str) -> str:
    """The student's name from the database, else from the roster."""
    row = students.get(student_id)
    return (
        (row["name"] if row else "")
        or roster_people(exam_id).get(student_id, {}).get("name", "")
        or student_id
    )


def fixes_for(exam_id: str) -> dict[str, str]:
    """Return the teacher's fixes as {sheet source: student id}."""
    path = exam_dir(exam_id) / "identity_fixes.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def set_fix(exam_id: str, source: str, student_id: str) -> None:
    """Attribute a sheet to a student by hand. The student must exist."""
    sid = students.clean(student_id)
    if students.get(sid) is None and sid not in roster_people(exam_id):
        raise ValueError(f"There is no student {sid!r}.")
    fixes = fixes_for(exam_id) | {source: sid}
    (exam_dir(exam_id) / "identity_fixes.json").write_text(
        json.dumps(fixes, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def clear_fix(exam_id: str, source: str) -> None:
    """Remove the teacher's fix for a sheet."""
    fixes = fixes_for(exam_id)
    fixes.pop(source, None)
    (exam_dir(exam_id) / "identity_fixes.json").write_text(
        json.dumps(fixes, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def choices(exam_id: str, entry: dict | None = None) -> list[tuple[str, str]]:
    """Return (student id, label) options for a fix.

    The likely candidates come first, then the course roster, then everyone else.
    """
    course_id = storage.load_meta(exam_id)["course_id"]
    order: list[str] = [c["student_id"] for c in (entry or {}).get("candidates", [])]
    if course_id is not None:
        order += [r["student_id"] for r in courses.roster(course_id)]
    order += list(roster_people(exam_id))
    order += [s["student_id"] for s in students.all_students()]
    seen: list[str] = []
    for sid in order:
        if sid not in seen:
            seen.append(sid)
    return [(sid, f"{sid} · {name_of(exam_id, sid)}") for sid in seen]

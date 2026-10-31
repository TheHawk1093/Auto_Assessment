"""Enrol the students found in an exam and give each an account, from an optional roster CSV.

The roster is a CSV with a header row: `student_id`, and optionally `name` and `email`. The student
id (roll number) is the unique key: it is what the answer files are named by. For each student found
in the marked exam this makes the student record, enrols them in the exam's course, and (if they
have no account) creates one whose username is the student id and whose first password is random,
shown once to the teacher to hand out. Students who already have an account, under whatever
username, are only enrolled.
"""

from __future__ import annotations

import csv
import io

from app.services import auth, courses, results, storage, students
from app.text import normalize

ID_COLUMNS = ("student_id", "id", "student", "username", "roll", "roll_no")


def parse_roster(data: bytes) -> dict[str, dict]:
    """Read the roster CSV into {student id: {name, email}}."""
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig")))
    fields = {(f or "").strip().lower(): f for f in reader.fieldnames or []}
    id_col = next((fields[c] for c in ID_COLUMNS if c in fields), None)
    if id_col is None:
        raise ValueError("The roster needs a header row with a student_id column.")
    out = {}
    for row in reader:
        sid = normalize(row.get(id_col) or "").strip()
        if sid:
            out[sid] = {
                "name": normalize(row.get(fields.get("name", ""), "") or "").strip(),
                "email": normalize(row.get(fields.get("email", ""), "") or "").strip(),
            }
    return out


def roster_file(exam_id: str):
    """Return the roster CSV uploaded with the answers, or None."""
    return next((p for p in storage.uploaded_files(exam_id, "answers") if p.suffix == ".csv"), None)


def _account_for(sid: str, rec: dict, by: str) -> tuple[str, str, str]:
    """(username, first password, status) for a student; makes the account if there is none."""
    username = students.account_of(sid)
    if username is not None:
        return username, "", "exists"
    password = auth.generate_password()
    try:
        auth.create_user(sid, "student", rec.get("name", ""), password, by=by, student_id=sid)
    except ValueError:  # the username (equal to the student id) belongs to someone else
        return "", "", "conflict"
    return sid, password, "created"


def _line(sid: str, username: str, password: str, status: str, enrolled: bool) -> dict:
    return {
        "student": sid,
        "name": students.name_of(sid),
        "username": username,
        "password": password,
        "status": status,
        "enrolled": enrolled,
    }


def create_accounts(exam_id: str, by: str) -> list[dict]:
    """Enrol and create accounts for the students found in a marked exam.

    Returns:
        One dict per student: {student, name, username, password, status, enrolled}. `status` is
        created, exists or conflict (the username was taken by someone else); `password` is set
        only for new accounts.
    """
    course_id = storage.load_meta(exam_id)["course_id"]
    path = roster_file(exam_id)
    info = parse_roster(path.read_bytes()) if path else {}
    out = []
    for raw in results.intake(exam_id).get("students", []):
        sid = students.clean(raw)
        rec = info.get(sid, {})
        students.ensure(sid, rec.get("name", ""), rec.get("email", ""))
        if course_id is not None:
            courses.enrol(course_id, sid, by)
        out.append(_line(sid, *_account_for(sid, rec, by), enrolled=course_id is not None))
    return out


def enrol_csv(course_id: int, data: bytes, by: str) -> list[dict]:
    """Enrol everyone in a roster CSV in a course and create missing accounts.

    Returns:
        The same shape as `create_accounts`.
    """
    out = []
    for sid, rec in parse_roster(data).items():
        courses.enrol(course_id, sid, by, rec["name"], rec["email"])
        out.append(_line(sid, *_account_for(sid, rec, by), enrolled=True))
    return out

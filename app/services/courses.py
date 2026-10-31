"""Courses and enrolments.

A course is one offering by one teacher (the same code taught by two teachers is two courses);
a student can be enrolled in any number of them, under one teacher, the other, or both. Exams
belong to a course (`exam.json` carries `course_id`), and a student sees an exam only while
enrolled in its course.
"""

from __future__ import annotations

import sqlite3

from app.services import db, notifications, storage, students
from app.text import normalize

_SELECT = (
    "SELECT c.id, c.code, c.title, c.term, c.teacher, u.name AS teacher_name "
    "FROM courses c JOIN users u ON u.username = c.teacher"
)


def create_course(code: str, title: str, teacher: str, term: str = "", by: str = "") -> int:
    """Create a course for a teacher and return its id.

    Raises:
        ValueError: If the code or title is empty, or the teacher already has this course.
    """
    code, title, term = (normalize(x).strip() for x in (code, title, term))
    if not code or not title:
        raise ValueError("A course needs a code and a title.")
    try:
        with db.connect() as c:
            cur = c.execute(
                "INSERT INTO courses (code, title, term, teacher) VALUES (?, ?, ?, ?)",
                (code, title, term, teacher),
            )
            course_id = cur.lastrowid
    except sqlite3.IntegrityError as e:
        raise ValueError(f"{teacher} already has a course {code} for this term.") from e
    db.audit(by or teacher, "create_course", f"{code} #{course_id}")
    return course_id


def update_course(course_id: int, title: str, term: str, by: str) -> None:
    """Rename a course or change its term. The code never changes: exams and records refer to it.

    Raises:
        ValueError: If the title is empty or the teacher already has this code for that term.
    """
    title, term = normalize(title).strip(), normalize(term).strip()
    if not title:
        raise ValueError("A course needs a title.")
    try:
        with db.connect() as c:
            c.execute(
                "UPDATE courses SET title = ?, term = ? WHERE id = ?", (title, term, course_id)
            )
    except sqlite3.IntegrityError as e:
        raise ValueError("This teacher already has the same course code in that term.") from e
    db.audit(by, "update_course", f"#{course_id}")


def get(course_id: int | None) -> dict | None:
    """Return the course with this id (with its teacher's name), or None."""
    if course_id is None:
        return None
    with db.connect() as c:
        row = c.execute(_SELECT + " WHERE c.id = ?", (course_id,)).fetchone()
    return dict(row) if row else None


def list_courses(teacher: str | None = None) -> list[dict]:
    """List courses, all or one teacher's, ordered by code."""
    with db.connect() as c:
        sql = _SELECT + (" WHERE c.teacher = ?" if teacher else "") + " ORDER BY c.code, c.teacher"
        rows = c.execute(sql, (teacher,) if teacher else ()).fetchall()
    return [dict(r) for r in rows]


def label(course: dict | None) -> str:
    """Short display name for a course, or 'No course'."""
    return f"{course['code']} · {course['title']}" if course else "No course"


def delete_course(course_id: int, by: str) -> None:
    """Remove a course that has no exams. Its enrolments go with it."""
    if any(m["course_id"] == course_id for m in storage.list_exams()):
        raise ValueError("This course still has exams. Delete or move them first.")
    with db.connect() as c:
        c.execute("DELETE FROM enrolments WHERE course_id = ?", (course_id,))
        c.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    db.audit(by, "delete_course", f"#{course_id}")


# ---------- enrolments ----------


def enrol(course_id: int, student_id: str, by: str, name: str = "", email: str = "") -> None:
    """Enrol a student (creating the student record if new). Re-enrols one who had dropped."""
    sid = students.ensure(student_id, name, email)
    with db.connect() as c:
        was = c.execute(
            "SELECT status FROM enrolments WHERE course_id = ? AND student_id = ?", (course_id, sid)
        ).fetchone()
        c.execute(
            "INSERT INTO enrolments (course_id, student_id, status, at)"
            " VALUES (?, ?, 'active', ?) ON CONFLICT (course_id, student_id)"
            " DO UPDATE SET status = 'active', at = excluded.at",
            (course_id, sid, db.now()),
        )
    db.audit(by, "enrol", f"{sid} in #{course_id}")
    if was is None or was["status"] != "active":
        course = get(course_id)
        if course:
            notifications.notify(
                students.account_of(sid), "enrolled", f"You were added to {label(course)}."
            )


def drop(course_id: int, student_id: str, by: str) -> None:
    """Mark the student as having left the course. Their marks are kept; they stop seeing it."""
    sid = students.clean(student_id)
    with db.connect() as c:
        c.execute(
            "UPDATE enrolments SET status = 'dropped', at = ?"
            " WHERE course_id = ? AND student_id = ?",
            (db.now(), course_id, sid),
        )
    db.audit(by, "drop", f"{sid} from #{course_id}")


def is_enrolled(course_id: int, student_id: str) -> bool:
    """Say whether the student is actively enrolled in the course."""
    with db.connect() as c:
        row = c.execute(
            "SELECT 1 FROM enrolments WHERE course_id = ? AND student_id = ? AND status = 'active'",
            (course_id, students.clean(student_id)),
        ).fetchone()
    return row is not None


def roster(course_id: int, include_dropped: bool = False) -> list[dict]:
    """The course's students: id, name, email, status and the account they sign in with."""
    sql = (
        "SELECT s.student_id, s.name, s.email, e.status, u.username FROM enrolments e "
        "JOIN students s ON s.student_id = e.student_id "
        "LEFT JOIN users u ON u.student_id = s.student_id WHERE e.course_id = ?"
    )
    if not include_dropped:
        sql += " AND e.status = 'active'"
    with db.connect() as c:
        return [dict(r) for r in c.execute(sql + " ORDER BY s.student_id", (course_id,)).fetchall()]


def courses_of(student_id: str, include_dropped: bool = False) -> list[dict]:
    """The courses a student is (or was) enrolled in, with the teacher of each."""
    sql = _SELECT + " JOIN enrolments e ON e.course_id = c.id WHERE e.student_id = ?"
    if not include_dropped:
        sql += " AND e.status = 'active'"
    with db.connect() as c:
        rows = c.execute(
            sql + " ORDER BY c.code, c.teacher", (students.clean(student_id),)
        ).fetchall()
    return [dict(r) for r in rows]

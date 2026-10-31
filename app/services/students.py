"""Students as people, separate from login accounts: one row per unique student id (roll number).

Answer files, results, regrade requests and enrolments all carry this id. An account links to it
through `users.student_id`; `account_of` finds the account, if the student has one yet.
"""

from __future__ import annotations

from app.services import db
from app.text import normalize


def clean(student_id: str) -> str:
    """Normalise a student id and strip spaces."""
    return normalize(student_id).strip()


def ensure(student_id: str, name: str = "", email: str = "") -> str:
    """Make sure the student exists and return the cleaned id.

    Fills in a missing name or email but never overwrites one that is already there.

    Raises:
        ValueError: If the id is empty.
    """
    sid = clean(student_id)
    if not sid:
        raise ValueError("A student id is required.")
    with db.connect() as c:
        c.execute(
            "INSERT OR IGNORE INTO students (student_id, name, email, created) VALUES (?, ?, ?, ?)",
            (sid, normalize(name).strip(), normalize(email).strip(), db.now()),
        )
        c.execute(
            "UPDATE students SET name = ? WHERE student_id = ? AND name = ''",
            (normalize(name).strip(), sid),
        )
        c.execute(
            "UPDATE students SET email = ? WHERE student_id = ? AND email = ''",
            (normalize(email).strip(), sid),
        )
    return sid


def update(student_id: str, name: str, email: str, by: str) -> None:
    """Change a student's name and email. The id (roll number) never changes.

    The name on the student's account follows, so every page shows the same one.

    Raises:
        ValueError: If there is no such student.
    """
    sid = clean(student_id)
    if get(sid) is None:
        raise ValueError(f"There is no student {sid!r}.")
    name, email = normalize(name).strip(), normalize(email).strip()
    with db.connect() as c:
        c.execute(
            "UPDATE students SET name = ?, email = ? WHERE student_id = ?", (name, email, sid)
        )
        c.execute("UPDATE users SET name = ? WHERE student_id = ?", (name, sid))
    db.audit(by, "update_student", sid)


def get(student_id: str) -> dict | None:
    """Return the student's row, or None."""
    with db.connect() as c:
        row = c.execute(
            "SELECT * FROM students WHERE student_id = ?", (clean(student_id),)
        ).fetchone()
    return dict(row) if row else None


def name_of(student_id: str) -> str:
    """Return the student's name, or the id if no name is known."""
    row = get(student_id)
    return (row["name"] if row else "") or clean(student_id)


def account_of(student_id: str) -> str | None:
    """The username that signs in as this student, or None if they have no account."""
    with db.connect() as c:
        row = c.execute(
            "SELECT username FROM users WHERE student_id = ?", (clean(student_id),)
        ).fetchone()
    return row["username"] if row else None


def all_students() -> list[dict]:
    """List every student with the username of their account, if any."""
    with db.connect() as c:
        rows = c.execute(
            "SELECT s.student_id, s.name, s.email, u.username FROM students s "
            "LEFT JOIN users u ON u.student_id = s.student_id ORDER BY s.student_id"
        ).fetchall()
    return [dict(r) for r in rows]

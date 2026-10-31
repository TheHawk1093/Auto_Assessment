"""SQLite for what is shared between people.

Covers accounts, students, courses, enrolments, mark overrides, regrade requests, notifications,
student submissions and the audit log. Exam files and marking output stay as files (see
storage.py). One small database, standard library only; `PATH` is module-level so tests can
point it at a temporary file.

Identity: a student is a row in `students`, keyed by a unique `student_id` (the roll number).
That id is what answer files are named by, what results and regrade requests carry, and what
enrolments refer to. A login account (`users`) links to it through `users.student_id`, so the
username a student signs in with is separate from who they are.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

from app import config

PATH = config.DB

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    student_id TEXT PRIMARY KEY,
    name       TEXT NOT NULL DEFAULT '',
    email      TEXT NOT NULL DEFAULT '',
    created    TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS users (
    username   TEXT PRIMARY KEY,
    role       TEXT NOT NULL CHECK (role IN ('admin', 'teacher', 'student')),
    name       TEXT NOT NULL DEFAULT '',
    pw_hash    TEXT NOT NULL,
    active     INTEGER NOT NULL DEFAULT 1,
    created    TEXT NOT NULL,
    student_id TEXT REFERENCES students (student_id)
);
CREATE TABLE IF NOT EXISTS courses (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    code    TEXT NOT NULL,
    title   TEXT NOT NULL,
    term    TEXT NOT NULL DEFAULT '',
    teacher TEXT NOT NULL REFERENCES users (username),
    UNIQUE (code, term, teacher)
);
CREATE TABLE IF NOT EXISTS enrolments (
    course_id  INTEGER NOT NULL REFERENCES courses (id),
    student_id TEXT NOT NULL REFERENCES students (student_id),
    status     TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'dropped')),
    at         TEXT NOT NULL,
    PRIMARY KEY (course_id, student_id)
);
CREATE TABLE IF NOT EXISTS overrides (
    exam_id  TEXT NOT NULL,
    student  TEXT NOT NULL,
    question TEXT NOT NULL,
    mark     REAL NOT NULL,
    comment  TEXT NOT NULL DEFAULT '',
    by_user  TEXT NOT NULL,
    at       TEXT NOT NULL,
    PRIMARY KEY (exam_id, student, question)
);
CREATE TABLE IF NOT EXISTS regrades (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_id      TEXT NOT NULL,
    student      TEXT NOT NULL,
    question     TEXT NOT NULL,
    kind         TEXT NOT NULL,
    reason       TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'pending'
                 CHECK (status IN ('pending', 'upheld', 'rejected')),
    old_mark     REAL,
    new_mark     REAL,
    reply        TEXT NOT NULL DEFAULT '',
    created      TEXT NOT NULL,
    decided_at   TEXT,
    decided_by   TEXT
);
CREATE TABLE IF NOT EXISTS notifications (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    kind     TEXT NOT NULL,
    text     TEXT NOT NULL,
    exam_id  TEXT NOT NULL DEFAULT '',
    created  TEXT NOT NULL,
    read     INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS ix_notifications_user ON notifications (username, read);
CREATE TABLE IF NOT EXISTS submissions (
    exam_id    TEXT NOT NULL,
    student_id TEXT NOT NULL REFERENCES students (student_id),
    files      TEXT NOT NULL,
    versions   INTEGER NOT NULL DEFAULT 1,
    at         TEXT NOT NULL,
    PRIMARY KEY (exam_id, student_id)
);
CREATE TABLE IF NOT EXISTS audit (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    at     TEXT NOT NULL,
    who    TEXT NOT NULL,
    action TEXT NOT NULL,
    detail TEXT NOT NULL DEFAULT ''
);
"""


def now() -> str:
    """Return the current local time as an ISO string to the second."""
    return datetime.now().isoformat(timespec="seconds")


def _migrate(conn: sqlite3.Connection) -> None:
    """Bring an older database up to date.

    An account made before students had their own ids is given one equal to its username, so
    what it owns (results, requests) still matches.
    """
    columns = {r["name"] for r in conn.execute("PRAGMA table_info(users)")}
    if "student_id" not in columns:
        conn.execute(
            "ALTER TABLE users ADD COLUMN student_id TEXT REFERENCES students (student_id)"
        )
    for row in conn.execute(
        "SELECT username, name FROM users WHERE role = 'student' AND student_id IS NULL"
    ):
        conn.execute(
            "INSERT OR IGNORE INTO students (student_id, name, created) VALUES (?, ?, ?)",
            (row["username"], row["name"], now()),
        )
        conn.execute(
            "UPDATE users SET student_id = ? WHERE username = ?", (row["username"], row["username"])
        )
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_users_student ON users (student_id)")


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """A connection that commits on success and always closes; rows behave like dicts."""
    PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        conn.executescript(SCHEMA)
        with conn:
            _migrate(conn)
            yield conn
    finally:
        conn.close()


def audit(who: str, action: str, detail: str = "") -> None:
    """Append an entry (who did what, with detail) to the audit log."""
    with connect() as c:
        c.execute(
            "INSERT INTO audit (at, who, action, detail) VALUES (?, ?, ?, ?)",
            (now(), who, action, detail),
        )

"""In-app notifications: a short message for one account, shown in the sidebar until read.

Nothing is sent outside the app. Services call `notify` when something a person should hear about
happens (results published, a regrade decided, a submission received). A student who has no account
yet has nobody to tell, so that case is skipped.
"""

from __future__ import annotations

from app.services import db, students

KINDS = {
    "published": "Results published",
    "regrade_decided": "Regrade decided",
    "regrade_asked": "Regrade requested",
    "mark_changed": "Mark changed",
    "submission": "Submission received",
    "job": "Job finished",
    "enrolled": "Added to a course",
    "assignment": "New assignment",
}


def notify(username: str | None, kind: str, text: str, exam_id: str = "") -> None:
    """Leave a message for one account. No account (e.g. a student who has none yet): nothing."""
    if not username:
        return
    with db.connect() as c:
        c.execute(
            "INSERT INTO notifications (username, kind, text, exam_id, created)"
            " VALUES (?, ?, ?, ?, ?)",
            (username, kind, text, exam_id, db.now()),
        )


def notify_students(student_ids, kind: str, text: str, exam_id: str = "") -> int:
    """Leave the same message for each student's account; return how many had one."""
    sent = 0
    for sid in student_ids:
        account = students.account_of(sid)
        if account:
            notify(account, kind, text, exam_id)
            sent += 1
    return sent


def unread_count(username: str) -> int:
    """How many messages the account has not read."""
    with db.connect() as c:
        row = c.execute(
            "SELECT COUNT(*) FROM notifications WHERE username = ? AND read = 0", (username,)
        ).fetchone()
    return row[0]


def recent(username: str, limit: int = 15) -> list[dict]:
    """The account's unread messages, newest first. A message that has been read is not shown."""
    with db.connect() as c:
        rows = c.execute(
            "SELECT * FROM notifications WHERE username = ? AND read = 0 ORDER BY id DESC LIMIT ?",
            (username, limit),
        ).fetchall()
    return [dict(r) for r in rows]


def mark_all_read(username: str) -> None:
    """Mark every message of the account as read."""
    with db.connect() as c:
        c.execute("UPDATE notifications SET read = 1 WHERE username = ?", (username,))

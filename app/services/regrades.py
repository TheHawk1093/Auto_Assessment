"""Regrade requests: a student asks, with a reason, within limits; the teacher decides.

The model never decides a regrade. The reason is data for the teacher to weigh, not an
instruction to anything; an upheld request becomes a teacher override (see grades.override), so
every figure a student sees still comes from one place.
"""

from __future__ import annotations

from datetime import date

from app.services import db, grades, notifications, publishing, storage, students
from app.text import normalize

KINDS = {
    "missed_point": "A point I made was not credited",
    "unfair_deduction": "Marks were taken off unfairly",
    "misread": "My answer was misread",
    "other": "Something else",
}


def _used(exam_id: str, student: str, refunds: bool) -> list[dict]:
    """Requests that count against the student's allowance."""
    with db.connect() as c:
        rows = c.execute(
            "SELECT * FROM regrades WHERE exam_id = ? AND student = ?", (exam_id, student)
        ).fetchall()
    return [dict(r) for r in rows if not (refunds and r["status"] == "rejected")]


def allowance(exam_id: str, student: str) -> dict:
    """What the student may still do: requests left in total and per question, and why not."""
    policy = storage.load_meta(exam_id)["policy"]
    used = _used(exam_id, student, policy["rejected_refunds"])
    per_q: dict[str, int] = {}
    for r in used:
        per_q[r["question"]] = per_q.get(r["question"], 0) + 1
    closed = ""
    if not policy["regrade_enabled"]:
        closed = "Regrade requests are not open for this exam."
    elif policy["regrade_deadline"] and date.today() > date.fromisoformat(
        policy["regrade_deadline"]
    ):
        closed = f"The deadline for requests was {policy['regrade_deadline']}."
    return {
        "closed": closed,
        "left": max(policy["regrade_max_total"] - len(used), 0),
        "max_total": policy["regrade_max_total"],
        "per_question_used": per_q,
        "per_question_max": policy["regrade_max_per_question"],
        "min_chars": policy["regrade_min_chars"],
    }


def submit(exam_id: str, student: str, question: str, kind: str, reason: str) -> int:
    """File a request and return its id. Raises ValueError with a message the student can read."""
    meta = storage.load_meta(exam_id)
    if not publishing.can_view(exam_id, student, meta):  # published, marked, and enrolled
        raise PermissionError("These results are not available.")
    allow = allowance(exam_id, student)
    reason = normalize(reason).strip()
    if allow["closed"]:
        raise ValueError(allow["closed"])
    if allow["left"] <= 0:
        raise ValueError(f"You have used all {allow['max_total']} of your regrade requests.")
    if allow["per_question_used"].get(question, 0) >= allow["per_question_max"]:
        raise ValueError(
            f"You have already asked about question {question} the most times allowed."
        )
    if kind not in KINDS:
        raise ValueError("Choose what you think went wrong.")
    if len(reason) < allow["min_chars"]:
        raise ValueError(
            f"Please explain in at least {allow['min_chars']} characters ({len(reason)} so far)."
        )
    marks = grades.final_marks(exam_id).get(student, {})
    if question not in marks:
        raise ValueError("That question was not marked.")
    with db.connect() as c:
        if c.execute(
            "SELECT 1 FROM regrades"
            " WHERE exam_id=? AND student=? AND question=? AND status='pending'",
            (exam_id, student, question),
        ).fetchone():
            raise ValueError("A request for this question is already waiting for the teacher.")
        cur = c.execute(
            "INSERT INTO regrades (exam_id, student, question, kind, reason, old_mark, created)"
            " VALUES (?, ?, ?, ?, ?, ?, ?)",
            (exam_id, student, question, kind, reason, marks[question], db.now()),
        )
        request_id = cur.lastrowid
    db.audit(student, "regrade_request", f"{exam_id} Q{question} #{request_id}")
    notifications.notify(
        meta["owner"], "regrade_asked",
        f"{students.name_of(student)} asked for a regrade of question {question} in "
        f"{meta['title']}.", exam_id,
    )  # fmt: skip
    return request_id


def list_requests(
    exam_id: str, student: str | None = None, status: str | None = None
) -> list[dict]:
    """List an exam's regrade requests, newest first, optionally of one student or status."""
    sql, args = "SELECT * FROM regrades WHERE exam_id = ?", [exam_id]
    if student is not None:
        sql, args = sql + " AND student = ?", [*args, student]
    if status:
        sql, args = sql + " AND status = ?", [*args, status]
    with db.connect() as c:
        return [dict(r) for r in c.execute(sql + " ORDER BY id DESC", args).fetchall()]


def decide(
    request_id: int, upheld: bool, reply: str, by: str, new_mark: float | None = None
) -> None:
    """Record the teacher's decision on a request.

    Upholding needs the new mark (it becomes an override); either way the student gets the reply.

    Raises:
        ValueError: If the request is not pending, the reply is empty, or an upheld request has
            no new mark.
    """
    reply = normalize(reply).strip()
    with db.connect() as c:
        row = c.execute("SELECT * FROM regrades WHERE id = ?", (request_id,)).fetchone()
    if row is None or row["status"] != "pending":
        raise ValueError("That request is not waiting for a decision.")
    if not reply:
        raise ValueError("Write a short reply for the student.")
    if upheld:
        if new_mark is None:
            raise ValueError("Enter the new mark.")
        current = grades.final_marks(row["exam_id"]).get(row["student"], {}).get(row["question"])
        if current is not None and abs(new_mark - current) < 1e-9:
            raise ValueError(
                f"The new mark is the same as the current mark ({current:g}). "
                "Enter the mark you want, or reject the request."
            )
        grades.override(
            row["exam_id"], row["student"], row["question"], new_mark, reply, by, notify=False
        )
    with db.connect() as c:
        c.execute(
            "UPDATE regrades SET status = ?, new_mark = ?, reply = ?,"
            " decided_at = ?, decided_by = ? WHERE id = ?",
            (
                "upheld" if upheld else "rejected",
                new_mark if upheld else None,
                reply,
                db.now(),
                by,
                request_id,
            ),
        )
    db.audit(by, "regrade_upheld" if upheld else "regrade_rejected", f"#{request_id}")
    meta = storage.load_meta(row["exam_id"])
    verdict = "the mark was changed" if upheld else "the mark was kept"
    notifications.notify(
        students.account_of(row["student"]), "regrade_decided",
        f"Your regrade request for question {row['question']} in {meta['title']}: {verdict}.",
        row["exam_id"],
    )  # fmt: skip


def pending_count(exam_id: str) -> int:
    """Count the exam's requests waiting for the teacher."""
    with db.connect() as c:
        row = c.execute(
            "SELECT COUNT(*) FROM regrades WHERE exam_id = ? AND status = 'pending'", (exam_id,)
        ).fetchone()
    return row[0]

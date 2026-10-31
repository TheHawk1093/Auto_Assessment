"""Work submitted by students, to be marked by the same pipeline as uploaded answer sheets.

A teacher opens submissions on an exam (optionally with a deadline). Enrolled students then
upload their own work: typed documents, photos or scans. Who submitted it is known from the
account, so it never depends on a roll number written on the page. When the window closes the
teacher collects the submissions into the exam's answer sheets: typed work becomes `<id>.md` with a
Name / Roll No header; photos become scanned sheets that carry the known identity into the
reader. From there the exam is prepared and marked as usual.
"""

from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path

from app.services import courses, db, notifications, scans, storage, students
from app.services.storage import exam_dir
from app.text import normalize
from autograde.intake.files import read_document

TYPED = {".txt", ".md", ".docx", ".pdf"}
ACCEPT = TYPED | scans.IMAGES
MAX_FILES = 30
MAX_BYTES = scans.MAX_BYTES


def folder(exam_id: str, student_id: str) -> Path:
    """Where one student's submission for an exam is kept."""
    return exam_dir(exam_id) / "submissions" / scans.safe(student_id)


def window(exam_id: str) -> tuple[bool, str]:
    """(open now, why not): the exam needs a course, an open window and a deadline not passed."""
    meta = storage.load_meta(exam_id)
    sub = meta["submissions"]
    if meta["course_id"] is None:
        return False, "This exam is not in a course."
    if not sub["open"]:
        return False, "Submissions are closed."
    if sub["deadline"] and date.today() > date.fromisoformat(sub["deadline"]):
        return False, f"The deadline was {sub['deadline']}."
    return True, ""


def open_window(exam_id: str, deadline: str, instructions: str, by: str) -> None:
    """Open (or update) the submission window and tell the enrolled students.

    Raises:
        ValueError: If the exam has no course, or the deadline is not a date.
    """
    meta = storage.load_meta(exam_id)
    if meta["course_id"] is None:
        raise ValueError("Put the exam in a course first: only its students can submit work.")
    if deadline:
        date.fromisoformat(deadline)  # ValueError names a bad date
    was_open = meta["submissions"]["open"]
    storage.update_submissions(
        exam_id, open=True, deadline=deadline, instructions=normalize(instructions).strip()
    )
    db.audit(by, "open_submissions", exam_id)
    if not was_open:
        later = f" Submit by {deadline}." if deadline else ""
        notifications.notify_students(
            [r["student_id"] for r in courses.roster(meta["course_id"])],
            "assignment",
            f"New assignment: {meta['title']}.{later}",
            exam_id,
        )


def close_window(exam_id: str, by: str) -> None:
    """Stop accepting hand-ins. What was submitted stays."""
    storage.update_submissions(exam_id, open=False)
    db.audit(by, "close_submissions", exam_id)


def open_for(student_id: str) -> list[dict]:
    """Exams in the student's courses that take submissions, or that they already submitted to."""
    mine = {c["id"] for c in courses.courses_of(student_id)}
    out = []
    for meta in storage.list_exams():
        if meta["course_id"] not in mine:
            continue
        is_open, _ = window(meta["id"])
        if is_open or status_of(meta["id"], student_id):
            out.append(meta)
    return out


def status_of(exam_id: str, student_id: str) -> dict | None:
    """The student's submission (files, when, how many times replaced), or None."""
    with db.connect() as c:
        row = c.execute(
            "SELECT * FROM submissions WHERE exam_id = ? AND student_id = ?",
            (exam_id, students.clean(student_id)),
        ).fetchone()
    if row is None:
        return None
    return {"files": json.loads(row["files"]), "at": row["at"], "versions": row["versions"]}


def submit(exam_id: str, student_id: str, files: list[tuple[str, bytes]]) -> list[str]:
    """Save the student's submission, replacing an earlier one, and tell the teacher.

    Raises:
        PermissionError: If the window is closed or the student is not enrolled in the course.
        ValueError: If nothing usable was uploaded or a file is too large.
    """
    sid = students.clean(student_id)
    meta = storage.load_meta(exam_id)
    is_open, why = window(exam_id)
    if not is_open:
        raise PermissionError(why)
    if not courses.is_enrolled(meta["course_id"], sid):
        raise PermissionError("You are not enrolled in this course.")
    good = [(Path(normalize(n)).name, d) for n, d in files if Path(n).suffix.lower() in ACCEPT]
    if not good:
        raise ValueError("Upload a document (txt, md, docx, pdf) or photos (png, jpg, webp).")
    if len(good) > MAX_FILES:
        raise ValueError(f"At most {MAX_FILES} files at a time.")
    if any(len(d) > MAX_BYTES for _, d in good):
        raise ValueError("A file is over 25 MB.")
    dest = folder(exam_id, sid)
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True)
    names = []
    for name, data in good:
        target = dest / name
        n = 2
        while target.exists():
            target = dest / f"{Path(name).stem}_{n}{Path(name).suffix}"
            n += 1
        target.write_bytes(data)
        names.append(target.name)
    before = status_of(exam_id, sid)
    with db.connect() as c:
        c.execute(
            "INSERT INTO submissions (exam_id, student_id, files, versions, at)"
            " VALUES (?, ?, ?, 1, ?) ON CONFLICT (exam_id, student_id) DO UPDATE SET"
            " files = excluded.files, versions = versions + 1, at = excluded.at",
            (exam_id, sid, json.dumps(names, ensure_ascii=False), db.now()),
        )
    db.audit(sid, "submit_work", f"{exam_id} {len(names)} file(s)")
    if before is None:  # one message per student, not one per replacement
        notifications.notify(
            meta["owner"],
            "submission",
            f"{students.name_of(sid)} submitted work for {meta['title']}.",
            exam_id,
        )
    return names


def roster_status(exam_id: str) -> list[dict]:
    """Every enrolled student with whether they submitted, plus anyone else who did."""
    meta = storage.load_meta(exam_id)
    with db.connect() as c:
        done = {r["student_id"]: r for r in c.execute(
            "SELECT * FROM submissions WHERE exam_id = ?", (exam_id,)).fetchall()}  # fmt: skip
    people = {r["student_id"]: r["name"] for r in courses.roster(meta["course_id"] or -1)}
    for sid in done:
        people.setdefault(sid, students.name_of(sid))
    return [
        {
            "student_id": sid,
            "name": name,
            "handed_in": sid in done,
            "at": done[sid]["at"] if sid in done else "",
            "files": json.loads(done[sid]["files"]) if sid in done else [],
            "versions": done[sid]["versions"] if sid in done else 0,
        }
        for sid, name in sorted(people.items())
    ]


def collect(exam_id: str, by: str) -> dict:
    """Turn every submission into answer sheets of the exam.

    A student's typed documents become `<id>.md` (with their identity in the header); if they
    submitted only photos or a scanned PDF, the pages go to the scans, to be read. Sheets this
    created earlier are replaced, so collecting again after a late submission is safe.

    Returns:
        {typed, scanned, skipped}: counts and a list of notes.
    """
    answers = storage.upload_dir(exam_id, "answers")
    answers.mkdir(parents=True, exist_ok=True)
    typed, scanned, skipped = 0, 0, []
    for row in roster_status(exam_id):
        if not row["handed_in"]:
            continue
        sid, name = row["student_id"], students.name_of(row["student_id"])
        mine = folder(exam_id, sid)
        docs = [mine / f for f in row["files"] if Path(f).suffix.lower() in TYPED]
        pics = [mine / f for f in row["files"] if Path(f).suffix.lower() in scans.IMAGES]
        texts = []
        for doc in docs:
            try:
                texts.append(read_document(doc).strip())
            except ValueError:  # a PDF with no text layer is a scan after all
                pics.append(doc)
        sheet = scans.safe(sid)
        if texts:
            scans.remove_sheet(exam_id, sheet)  # photos from an earlier submission no longer count
            body = "\n\n".join(t for t in texts if t)
            (answers / f"{sheet}.md").write_text(
                f"Name: {name}\nRoll No: {sid}\n\n{body}\n", encoding="utf-8"
            )
            typed += 1
            if pics:
                skipped.append(f"{sid}: photos ignored because a typed document was submitted.")
        elif pics:
            scans.remove_sheet(exam_id, sheet)  # replace what an earlier collect added
            files, count = [], 0
            for pic in pics:
                if pic.suffix.lower() == ".pdf":  # rasterized under the sheet's own name
                    files.append((f"{sheet}.pdf", pic.read_bytes()))
                else:
                    count += 1
                    files.append((f"{sheet}_p{count}{pic.suffix}", pic.read_bytes()))
            added, bad = scans.add(exam_id, files, known={sheet: {"student_id": sid, "name": name}})
            skipped += [f"{sid}: {b}" for b in bad]
            scanned += 1 if added else 0
    db.audit(by, "collect_submissions", f"{exam_id} typed={typed} scanned={scanned}")
    return {"typed": typed, "scanned": scanned, "skipped": skipped}

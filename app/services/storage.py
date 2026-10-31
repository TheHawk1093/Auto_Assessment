"""Exams on disk: one folder per exam holding its uploads, settings and job state.

No database yet; accounts and linking come later. Everything the UI needs is in
app_data/exams/<id>/exam.json, so the folder can be inspected or deleted by hand.
"""

from __future__ import annotations

import io
import json
import re
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

from app import config
from app.services import models, settings_spec
from app.text import normalize

# Module-level so tests can point them at a temporary folder.
EXAMS = config.EXAMS
RUNS = config.RUNS


def exam_dir(exam_id: str) -> Path:
    """Return the exam's folder under app_data."""
    return EXAMS / exam_id


def run_name(exam_id: str) -> str:
    """Return the name of the exam's marking run."""
    return f"app_{exam_id}"


def run_path(exam_id: str) -> Path:
    """Return the folder holding the exam's marking output."""
    return RUNS / run_name(exam_id)


# What students may do once results are published. Edited on the Publish tab.
DEFAULT_POLICY: dict = {
    "show_answer": True,  # the student sees their own answer next to the feedback
    "show_reference": False,  # ... and the teacher's model answer
    "regrade_enabled": True,
    "regrade_max_total": 2,  # requests per student in the whole exam
    "regrade_max_per_question": 1,
    "regrade_min_chars": 40,  # the reason must say something
    "regrade_deadline": "",  # YYYY-MM-DD, last day to ask; empty means no limit
    "rejected_refunds": False,  # a rejected request does not use up an attempt when True
}


# Submissions: the teacher opens a window in which enrolled students upload their own work.
DEFAULT_SUBMISSIONS: dict = {
    "open": False,
    "deadline": "",  # YYYY-MM-DD, the last day to submit; empty means no limit
    "instructions": "",  # shown to students beside the upload box
}


def list_exams(owner: str | None = None) -> list[dict]:
    """All exams, newest first; only the owner's when `owner` is given."""
    if not EXAMS.exists():
        return []
    metas = [load_meta(p.name) for p in EXAMS.iterdir() if (p / "exam.json").exists()]
    if owner is not None:
        metas = [m for m in metas if m["owner"] == owner]
    return sorted(metas, key=lambda m: m["created"], reverse=True)


def create_exam(
    title: str, owner: str = "", exam_id: str | None = None, course_id: int | None = None
) -> str:
    """A new exam folder. The id is made from the title and the time unless one is given."""
    title = normalize(title).strip()
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:30] or "exam"
    exam_id = exam_id or f"{slug}-{datetime.now():%y%m%d-%H%M%S}"
    exam_dir(exam_id).mkdir(parents=True)
    save_meta(
        exam_id,
        {
            "id": exam_id,
            "title": title,
            "created": datetime.now().isoformat(timespec="seconds"),
            "owner": owner,
            "course_id": course_id,  # the offering this exam belongs to (courses table)
            "published": None,  # timestamp once the teacher publishes the results
            "model": models.DEFAULT,  # id from services/models.CATALOGUE
            "policy": dict(DEFAULT_POLICY),
            "settings": settings_spec.defaults(),
            "reader": models.DEFAULT_READER,  # who reads handwritten or scanned sheets
            "submissions": dict(DEFAULT_SUBMISSIONS),
        },
    )
    return exam_id


def delete_exam(exam_id: str) -> None:
    """Remove the exam, its uploads and its marking run."""
    shutil.rmtree(exam_dir(exam_id), ignore_errors=True)
    shutil.rmtree(run_path(exam_id), ignore_errors=True)


def load_meta(exam_id: str) -> dict:
    """Read exam.json, filling in defaults for anything an older file lacks."""
    meta = json.loads((exam_dir(exam_id) / "exam.json").read_text(encoding="utf-8"))
    meta["settings"] = {**settings_spec.defaults(), **meta.get("settings", {})}
    meta["policy"] = {**DEFAULT_POLICY, **meta.get("policy", {})}
    meta["submissions"] = {**DEFAULT_SUBMISSIONS, **meta.get("submissions", {})}
    meta.setdefault("reader", models.DEFAULT_READER)
    meta.setdefault("owner", "")
    meta.setdefault("course_id", None)
    meta.setdefault("published", None)
    meta.setdefault("model", models.DEFAULT)
    return meta


def save_meta(exam_id: str, meta: dict) -> None:
    """Write exam.json."""
    (exam_dir(exam_id) / "exam.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def update_settings(exam_id: str, **changes) -> None:
    """Merge changes into the exam's marking settings."""
    meta = load_meta(exam_id)
    meta["settings"].update(changes)
    save_meta(exam_id, meta)


def update_policy(exam_id: str, **changes) -> None:
    """Merge changes into what students may do once results are published."""
    meta = load_meta(exam_id)
    meta["policy"].update(changes)
    save_meta(exam_id, meta)


def update_submissions(exam_id: str, **changes) -> None:
    """Merge changes into the exam's submission window (open, deadline, instructions)."""
    meta = load_meta(exam_id)
    meta["submissions"].update(changes)
    save_meta(exam_id, meta)


def set_reader(exam_id: str, option_id: str) -> None:
    """Choose the reader for handwritten and scanned sheets."""
    meta = load_meta(exam_id)
    meta["reader"] = option_id
    save_meta(exam_id, meta)


def rename_exam(exam_id: str, title: str) -> None:
    """Change the exam's title. Its id, folder and marks stay as they are."""
    title = normalize(title).strip()
    if not title:
        raise ValueError("An exam needs a title.")
    meta = load_meta(exam_id)
    meta["title"] = title
    save_meta(exam_id, meta)


def set_course(exam_id: str, course_id: int | None) -> None:
    """Move the exam into a course (or out of any, with None)."""
    meta = load_meta(exam_id)
    meta["course_id"] = course_id
    save_meta(exam_id, meta)


def set_model(exam_id: str, option_id: str) -> None:
    """Choose the AI model option that marks the exam."""
    meta = load_meta(exam_id)
    meta["model"] = option_id
    save_meta(exam_id, meta)


def set_published(exam_id: str, published: bool) -> None:
    """Set or clear the exam's publication time."""
    meta = load_meta(exam_id)
    meta["published"] = datetime.now().isoformat(timespec="seconds") if published else None
    save_meta(exam_id, meta)


def exam_status(exam_id: str) -> str:
    """Draft (files missing), ready, prepared (schemes written), marked or published."""
    run = run_path(exam_id)
    if (run / "marks.csv").exists():
        return "published" if load_meta(exam_id)["published"] else "marked"
    if (run / "intake.json").exists():
        return "prepared"
    answers = [p for p in uploaded_files(exam_id, "answers") if p.suffix.lower() != ".csv"]
    if uploaded_files(exam_id, "paper") and (answers or uploaded_files(exam_id, "scans")):
        return "ready"
    return "draft"


# ---------- uploads ----------


def upload_dir(exam_id: str, section: str) -> Path:
    """Return the folder for one upload section (paper, reference or answers)."""
    return exam_dir(exam_id) / "uploads" / section


def uploaded_files(exam_id: str, section: str) -> list[Path]:
    """List the files uploaded in a section, sorted by name."""
    d = upload_dir(exam_id, section)
    return sorted(p for p in d.iterdir() if p.is_file()) if d.exists() else []


def _unique(dest: Path, name: str) -> Path:
    name = normalize(name)  # zips from macOS name files in NFD, Windows in NFC
    path = dest / name
    n = 2
    while path.exists():
        path = dest / f"{Path(name).stem}_{n}{Path(name).suffix}"
        n += 1
    return path


def _extract_zip(data: bytes, dest: Path, allowed: set[str]) -> tuple[list[str], list[str]]:
    """Flatten a zip into dest, returning (saved names, skipped names).

    Only the file's base name is used, so a path like ../x cannot escape the folder.
    """
    saved, skipped, total = [], [], 0
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            name = Path(info.filename).name
            if info.is_dir() or not name or name.startswith((".", "~$")):
                continue
            if "__MACOSX" in info.filename or Path(name).suffix.lower() not in allowed:
                skipped.append(info.filename)
                continue
            total += info.file_size
            if total > config.MAX_ZIP_BYTES:
                raise ValueError("The zip is larger than 300 MB when unpacked.")
            target = _unique(dest, name)
            target.write_bytes(z.read(info))
            saved.append(target.name)
    return saved, skipped


def save_uploads(
    exam_id: str, section: str, files: list[tuple[str, bytes]], allow_zip: bool, extra: set[str]
) -> tuple[list[str], list[str]]:
    """Replace a section's files with the uploaded ones.

    A .zip is unpacked when allowed.

    Args:
        exam_id: The exam.
        section: paper, reference or answers.
        files: (name, bytes) pairs.
        allow_zip: Whether a .zip is unpacked rather than skipped.
        extra: Extra suffixes to accept beyond the document types, such as {".csv"}.

    Returns:
        (saved names, skipped names).
    """
    dest = upload_dir(exam_id, section)
    clear_section(exam_id, section)
    dest.mkdir(parents=True, exist_ok=True)
    allowed = config.DOC_EXT | extra
    saved, skipped = [], []
    for name, data in files:
        suffix = Path(name).suffix.lower()
        if suffix == ".zip" and allow_zip:
            try:
                s, k = _extract_zip(data, dest, allowed)
            except zipfile.BadZipFile:
                skipped.append(f"{name} (not a valid zip)")
                continue
            saved += s
            skipped += k
        elif suffix in allowed:
            target = _unique(dest, Path(name).name)
            target.write_bytes(data)
            saved.append(target.name)
        else:
            skipped.append(name)
    return saved, skipped


def clear_section(exam_id: str, section: str) -> None:
    """Delete every file uploaded in a section."""
    for p in uploaded_files(exam_id, section):
        p.unlink()

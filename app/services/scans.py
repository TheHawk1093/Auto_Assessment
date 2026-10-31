"""Scanned and photographed answer sheets.

Images (and PDFs, which are turned into one image per page) are kept in the exam's `scans`
folder. The `autograde scan` job reads each sheet into a text document, `<sheet>.md`, saved with
the other answer files, so from there on a scan is marked exactly like a typed answer: the
roll number and name written on it are matched to the student database, and the teacher can
correct what the reader got wrong before marking. Pages of one sheet share a name:
`scan_01_p1.jpg`, `scan_01_p2.jpg`; a lone image is a sheet of its own.
"""

from __future__ import annotations

import io
import json
import re
import zipfile
from pathlib import Path

from app.services import storage
from app.text import normalize
from autograde.ocr.answersheet import unsure_count, word_count
from autograde.ocr.sheets import PAGE, group_pages

IMAGES = {".png", ".jpg", ".jpeg", ".webp"}
TYPES = IMAGES | {".pdf"}
MAX_PAGES = 40  # per PDF
MAX_BYTES = 25 * 1024 * 1024  # per uploaded file
SUMMARY = "_scan.json"  # what the last read job found, kept beside the images
IDENTITIES = "_identities.json"  # sheets whose writer is already known (submitted by a student)


def folder(exam_id: str) -> Path:
    """The exam's folder of page images."""
    return storage.upload_dir(exam_id, "scans")


def _answers(exam_id: str) -> Path:
    return storage.upload_dir(exam_id, "answers")


def safe(name: str) -> str:
    """A file-name-safe form of a student id or sheet name."""
    return re.sub(r"[^\w.\-]+", "_", normalize(name)).strip("._") or "sheet"


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


# ---------- adding pages ----------


def rasterize(pdf: bytes, stem: str, dest: Path) -> list[str]:
    """Save each page of a PDF as `<stem>_p<n>.png` in `dest`; return the file names."""
    import pypdfium2 as pdfium

    document = pdfium.PdfDocument(pdf)
    names = []
    try:
        for i in range(min(len(document), MAX_PAGES)):
            page = document[i]
            name = f"{stem}_p{i + 1}.png"
            page.render(scale=2).to_pil().save(dest / name)
            names.append(name)
    finally:
        document.close()
    return names


def _free_stem(dest: Path, stem: str) -> str:
    """A sheet name not used yet, so a second upload never overwrites the first."""
    taken = set(group_pages(dest))
    name, n = stem, 2
    while name in taken:
        name, n = f"{stem}_{n}", n + 1
    return name


def add(
    exam_id: str, files: list[tuple[str, bytes]], known: dict | None = None
) -> tuple[list, list]:
    """Add page images to the exam. A .zip is unpacked; a PDF becomes one image per page.

    Args:
        exam_id: The exam.
        files: (name, bytes) pairs.
        known: {sheet name: {student_id, name}} for sheets whose writer is known.

    Returns:
        (sheets added, skipped names with the reason).
    """
    dest = folder(exam_id)
    dest.mkdir(parents=True, exist_ok=True)
    added: list[str] = []
    skipped: list[str] = []

    def take(name: str, data: bytes) -> None:
        stem, suffix = Path(normalize(name)).stem, Path(name).suffix.lower()
        if suffix not in TYPES:
            skipped.append(f"{name} (not an image or PDF)")
        elif len(data) > MAX_BYTES:
            skipped.append(f"{name} (over 25 MB)")
        elif suffix == ".pdf":
            sheet = _free_stem(dest, safe(stem))
            try:
                if rasterize(data, sheet, dest):
                    added.append(sheet)
            except Exception as exc:  # noqa: BLE001 - a damaged PDF is the teacher's to replace
                skipped.append(f"{name} (could not open the PDF: {exc})")
        else:
            m = PAGE.match(stem)
            sheet = safe(m["sheet"] if m else stem)
            page = f"_p{m['page']}" if m else "_p1"
            target = dest / f"{sheet}{page}{suffix}"
            if target.exists():  # a different picture with the same name
                sheet = _free_stem(dest, sheet)
                target = dest / f"{sheet}{page}{suffix}"
            target.write_bytes(data)
            if sheet not in added:
                added.append(sheet)

    for name, data in files:
        if Path(name).suffix.lower() == ".zip":
            try:
                with zipfile.ZipFile(io.BytesIO(data)) as z:
                    total = 0
                    for info in z.infolist():
                        base = Path(info.filename).name
                        if info.is_dir() or not base or base.startswith((".", "~$")):
                            continue
                        if "__MACOSX" in info.filename:
                            continue
                        total += info.file_size
                        if total > 300 * 1024 * 1024:
                            raise ValueError("The zip is larger than 300 MB when unpacked.")
                        take(base, z.read(info))
            except zipfile.BadZipFile:
                skipped.append(f"{name} (not a valid zip)")
        else:
            take(Path(name).name, data)
    if known:
        mapping = _json(dest / IDENTITIES) | known
        (dest / IDENTITIES).write_text(json.dumps(mapping, ensure_ascii=False), encoding="utf-8")
    return added, skipped


def divert_unreadable_pdfs(exam_id: str) -> list[str]:
    """Move PDFs in the typed-answers folder that have no text layer (scans) over to the scans.

    Returns the file names moved. A PDF with a text layer stays where it is.
    """
    from pypdf import PdfReader

    moved = []
    for path in storage.uploaded_files(exam_id, "answers"):
        if path.suffix.lower() != ".pdf":
            continue
        try:
            text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
        except Exception:  # noqa: BLE001 - unreadable as text: treat as a scan
            text = ""
        if len(text.strip()) >= 20:
            continue
        added, _ = add(exam_id, [(path.name, path.read_bytes())])
        if added:
            path.unlink()
            moved.append(path.name)
    return moved


# ---------- what is there ----------


def sheets(exam_id: str) -> dict[str, list[Path]]:
    """The page images by sheet, in page order."""
    d = folder(exam_id)
    return group_pages(d) if d.exists() else {}


def transcript_path(exam_id: str, sheet: str) -> Path:
    """Where the sheet's text document is (or will be) kept: with the answers."""
    return _answers(exam_id) / f"{sheet}.md"


def rows(exam_id: str) -> list[dict]:
    """One dict per sheet: its pages, whether it has been read, and what the reader found."""
    summary = _json(folder(exam_id) / SUMMARY)
    known = _json(folder(exam_id) / IDENTITIES)
    out = []
    for name, pages in sheets(exam_id).items():
        path = transcript_path(exam_id, name)
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        info = summary.get(name, {})
        out.append(
            {
                "sheet": name,
                "pages": pages,
                "read": path.exists(),
                "text": text,
                "words": word_count(text) if text else 0,
                "unsure": unsure_count(text) if text else 0,
                "reader": info.get("reader", ""),
                "error": info.get("error", "") if info.get("status") == "failed" else "",
                "known": known.get(name),
            }
        )
    return out


def unread(exam_id: str) -> list[str]:
    """The sheets that have no text document yet."""
    return [r["sheet"] for r in rows(exam_id) if not r["read"]]


def identities_file(exam_id: str) -> Path | None:
    """The file naming the known writers, if any."""
    p = folder(exam_id) / IDENTITIES
    return p if p.exists() else None


def summary_file(exam_id: str) -> Path:
    """Where the read job records what it found."""
    return folder(exam_id) / SUMMARY


# ---------- correcting and removing ----------


def save_transcript(exam_id: str, sheet: str, text: str) -> None:
    """Replace the document read from a sheet with the teacher's corrected text."""
    if sheet not in sheets(exam_id):
        raise ValueError(f"There is no scanned sheet {sheet!r}.")
    transcript_path(exam_id, sheet).write_text(normalize(text).strip() + "\n", encoding="utf-8")


def forget_read(exam_id: str, sheet: str) -> None:
    """Throw away the text read from a sheet so the next read job does it again."""
    transcript_path(exam_id, sheet).unlink(missing_ok=True)
    path = summary_file(exam_id)
    summary = _json(path)
    if summary.pop(sheet, None) is not None:
        path.write_text(json.dumps(summary), encoding="utf-8")


def remove_sheet(exam_id: str, sheet: str) -> None:
    """Delete a sheet's images and the text read from it."""
    for page in sheets(exam_id).get(sheet, []):
        page.unlink(missing_ok=True)
    forget_read(exam_id, sheet)
    path = folder(exam_id) / IDENTITIES
    known = _json(path)
    if known.pop(sheet, None) is not None:
        path.write_text(json.dumps(known), encoding="utf-8")


def pages_for(exam_id: str, student_id: str) -> list[Path]:
    """The original page images of the student's scanned sheet, if their answer came from one.

    Found through the identity report: the sheet whose text was attributed to this student.
    """
    from app.services import identity

    have = sheets(exam_id)
    for entry in identity.report(exam_id):
        if entry["student_id"] == student_id and Path(entry["source"]).stem in have:
            return have[Path(entry["source"]).stem]
    return []

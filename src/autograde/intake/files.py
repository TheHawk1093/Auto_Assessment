"""Read the text out of the files a teacher is likely to have."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

from autograde.intake.figures import anchor_figures, docx_pictures

TEXT = {".txt", ".md", ".json", ".jsonl", ".csv", ".tex"}


def read_document(path: Path) -> str:
    """Plain text of a .txt, .md, .json, .csv, .docx or text-based .pdf file."""
    suffix = path.suffix.lower()
    if suffix in TEXT:
        return anchor_figures(path.read_text(encoding="utf-8"), path.parent)
    if suffix == ".docx":
        return _docx_text(path)
    if suffix == ".pdf":
        return _pdf_text(path)
    raise ValueError(f"Cannot read {path.name}: use txt, md, json, csv, docx or pdf.")


def _docx_text(path: Path) -> str:
    """Paragraph text; a picture is saved next to the file and appears as a `[figure: ...]` line."""
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
        pictures = docx_pictures(zf, xml)
        media = path.parent / f"{path.stem}_media"
        paragraphs = re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.DOTALL)
        lines = []
        for i, para in enumerate(paragraphs):
            para = re.sub(r"<w:tab/>", "\t", para)
            text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", para))
            lines.append(_unescape(text))
            for name in pictures.get(i, []):
                media.mkdir(exist_ok=True)
                out = media / Path(name).name
                out.write_bytes(zf.read(name))
                lines.append(f"[figure: {out.resolve().as_posix()}]")
    return "\n".join(lines)


def _unescape(text: str) -> str:
    for a, b in (("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"'), ("&apos;", "'"), ("&amp;", "&")):
        text = text.replace(a, b)
    return text


def _pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise ValueError("Reading PDF files needs pypdf: pip install pypdf") from exc
    text = "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    if len(text.strip()) < 20:
        raise ValueError(f"{path.name} has no text layer (a scan). Read it with `autograde ocr`.")
    return text

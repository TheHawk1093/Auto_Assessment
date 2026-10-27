"""Read the text out of the files a teacher is likely to have."""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

TEXT = {".txt", ".md", ".json", ".jsonl", ".csv", ".tex"}


def read_document(path: Path) -> str:
    """Plain text of a .txt, .md, .json, .csv, .docx or text-based .pdf file."""
    suffix = path.suffix.lower()
    if suffix in TEXT:
        return path.read_text(encoding="utf-8")
    if suffix == ".docx":
        return _docx_text(path)
    if suffix == ".pdf":
        return _pdf_text(path)
    raise ValueError(f"Cannot read {path.name}: use txt, md, json, csv, docx or pdf.")


def _docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8")
    paragraphs = re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.DOTALL)
    lines = []
    for para in paragraphs:
        para = re.sub(r"<w:tab/>", "\t", para)
        text = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", para))
        lines.append(_unescape(text))
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

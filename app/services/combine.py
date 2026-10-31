"""Several files as one document for the pipeline.

A question paper can be a zip of files, and a student's submission can be a zip of code and a
report. The marking command takes one document per paper and per student, so the files are joined:
code in fenced blocks, notebooks as their cells, reports as their text. A file whose name starts
with a question number (`q1.py`, `Q2a_notes.md`) is placed under that question; when every file of
a submission is named that way the split into answers is done by code, otherwise the pipeline's
splitter reads the whole text and decides.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from app import config
from autograde.intake.files import read_document

LANG = {
    ".py": "python", ".java": "java", ".c": "c", ".cpp": "cpp", ".h": "c", ".js": "javascript",
    ".ts": "typescript", ".cs": "csharp", ".go": "go", ".rs": "rust", ".m": "matlab", ".r": "r",
    ".sql": "sql", ".sh": "bash", ".ipynb": "python",
}  # fmt: skip
assert set(LANG) == config.CODE_EXT, "config.CODE_EXT and combine.LANG must list the same types"

QUESTION_FILE = re.compile(r"^(?:question|ques|q)[ _\-]*(\d+[a-z]?)(?![a-z0-9])", re.IGNORECASE)


def question_of(name: str) -> str | None:
    """The question a file is named for: `q1.py` gives 1, `Q2a_report.md` gives 2a, else None."""
    m = QUESTION_FILE.match(Path(name).stem)
    return m.group(1).lower() if m else None


def _notebook(path: Path) -> str:
    cells = json.loads(path.read_text(encoding="utf-8")).get("cells", [])
    parts = []
    for cell in cells:
        text = "".join(cell.get("source", []))
        if not text.strip():
            continue
        parts.append(f"```python\n{text}\n```" if cell.get("cell_type") == "code" else text)
    return "\n\n".join(parts)


def file_text(path: Path) -> str:
    """The text of one file: code fenced, a notebook as cells, a document as its text.

    Raises:
        ValueError: If the file cannot be read as text (a scanned PDF, a picture).
    """
    suffix = path.suffix.lower()
    if suffix == ".ipynb":
        return _notebook(path)
    if suffix in LANG:
        code = path.read_text(encoding="utf-8", errors="replace").rstrip()
        return f"```{LANG[suffix]}\n{code}\n```"
    return read_document(path).strip()


def combine(files: list[Path], by_question: bool = True) -> tuple[str, list[str]]:
    """Join files into one document; return it and the names that could not be read.

    Every file is shown under `## File: name`. If all files carry a question number in their name
    they are laid out as `Q<id>.` sections instead, ready for a plain split (`by_question`).
    """
    named = {f: question_of(f.name) for f in files}
    by_question = by_question and all(named.values()) and bool(files)
    unreadable: list[str] = []
    parts: list[tuple[str, str]] = []
    for f in sorted(files, key=lambda p: (named[p] or "~", p.name.lower())):
        try:
            parts.append((f.name, file_text(f)))
        except (ValueError, OSError, json.JSONDecodeError):
            unreadable.append(f.name)
            continue
    if by_question:
        out = [f"Q{named[next(f for f in files if f.name == n)]}.\n{t}" for n, t in parts]
    else:
        out = [f"## File: {n}\n\n{t}" for n, t in parts]
    return "\n\n".join(out), unreadable

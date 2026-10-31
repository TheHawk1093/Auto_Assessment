"""Read a student's answer sheet into a text document the exam command can mark.

The document is a Name / Roll No header, then one `Q<number>.` section per answer.

This is the entry for sheets that carry only the student's writing. `sheets.py` is the other
track, for sheets that already show the printed questions and a teacher's marks. The text keeps
`[?word?]` where the reader was unsure, so a person can check those spots before marking.
"""

from __future__ import annotations

import re
from pathlib import Path

from autograde import prompts
from autograde.config import LLMConfig
from autograde.llm import build_client
from autograde.llm.base import LLMError
from autograde.ocr.hosted import PROVIDERS
from autograde.ocr.readers import INDIC_SHARE, is_indic
from autograde.ocr.transcribe import UNSURE, cli_read

PAPER_LIMIT = 6000  # characters of the question paper shown to the reader, to learn the numbering
HEADER = re.compile(r"^\s*(name|roll\s*(no\.?|number)?|student\s*id)\s*[:\-]", re.IGNORECASE)


def read_answer_sheet(
    pages: list[Path], provider: str, model: str, paper_text: str = "", effort: str | None = None
) -> str:
    """Transcribe the pages of one sheet with the given reader and return the document text."""
    user = f"The sheet has {len(pages)} page image(s), in order."
    if paper_text.strip():
        user += (
            "\n\nQuestion paper, only to learn how the questions are numbered:\n"
            + paper_text.strip()[:PAPER_LIMIT]
        )
    system = prompts.system("ocr.answersheet")
    if provider == "claude_cli":
        client = build_client(LLMConfig(backend="claude_cli", model=model, effort=effort))
        files = "\n".join(f"Page {i}: {p.resolve()}" for i, p in enumerate(pages, 1))
        text, usage = cli_read(pages, client, system, f"{user}\nOpen each one:\n{files}")
    elif provider in PROVIDERS:
        text = PROVIDERS[provider](pages, model, system, user)
    else:
        raise LLMError(f"Unknown reader {provider!r}")
    text = _plain(_unfence(text))
    if not text.strip():
        raise LLMError("The reader returned nothing for this sheet.")
    return text


def looks_indic(text: str) -> bool:
    """True when most letters are in an Indian script (pages for the Indic specialist)."""
    letters = [c for c in text if c.isalpha()]
    return len(letters) >= 5 and sum(is_indic(c) for c in letters) / len(letters) >= INDIC_SHARE


def _plain(text: str) -> str:
    """Turn the HTML tables a document parser returns into lines of words."""
    if "<t" not in text:
        return text
    text = re.sub(r"</t[dh]>\s*", " ", text)
    text = re.sub(r"</tr>\s*", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    return "\n".join(" ".join(line.split()) for line in text.splitlines()).strip()


def _unfence(text: str) -> str:
    text = text.strip()
    m = re.match(r"^```[a-z]*\n(.*?)\n```$", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


def with_identity(text: str, student_id: str, name: str = "") -> str:
    """The document with its Name / Roll No header replaced by a known identity.

    Used for work a signed-in student handed in: who they are is known, so it does not depend on
    what the reader made of their handwriting.
    """
    lines = text.splitlines()
    top = 0
    while top < len(lines) and top < 6 and (HEADER.match(lines[top]) or not lines[top].strip()):
        top += 1
    body = "\n".join(lines[top:]).lstrip("\n")
    head = (f"Name: {name}\n" if name else "") + f"Roll No: {student_id}\n"
    return f"{head}\n{body}\n"


def unsure_count(text: str) -> int:
    """How many spans the reader marked as unclear."""
    return len(UNSURE.findall(text))


def word_count(text: str) -> int:
    """Words in the document, header excluded."""
    return len(" ".join(x for x in text.splitlines() if not HEADER.match(x)).split())

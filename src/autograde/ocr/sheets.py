"""Turn photos of a marked answer sheet into grader items.

All pages of one sheet go to the model in one call, because questions and answers run across
page breaks. The model returns one entry per question: printed question, the student's writing,
the marks the question is worth, and the teacher's mark when one is written. `to_items` maps
those entries onto `Item`, so the existing pipeline can grade them.

Model answers are not on a student sheet. They come from an optional key file; without one the
`model_answer` is empty and must be supplied before marking.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from autograde import prompts
from autograde.llm.base import LLMClient, LLMError
from autograde.ocr.transcribe import MEDIA, UNSURE, cli_read
from autograde.schemas import Item

PAGE = re.compile(r"^(?P<sheet>.+?)[_ -]*p(?:age)?[_ -]*(?P<page>\d+)$", re.IGNORECASE)


class SheetItem(BaseModel):
    question_id: str
    page: int | None = None
    question: str = ""
    max_mark: float | None = None
    student_answer: str = ""
    teacher_mark: float | None = None
    unsure: list[str] = Field(default_factory=list)


class Sheet(BaseModel):
    sheet: str = ""
    student: str = ""
    pages: list[str] = Field(default_factory=list)
    reader: str = Field(
        default="", description="The model that read these pages, as provider:model."
    )
    teacher_totals: dict[str, float] = Field(
        default_factory=dict, description="Teacher's mark per whole question, by printed number."
    )
    items: list[SheetItem]


def group_pages(folder: str | Path, per_page: bool = False) -> dict[str, list[Path]]:
    """Images in `folder` grouped by sheet, in page order. `German_p2.jpeg` is page 2 of German.

    With `per_page`, every image is its own sheet named after the file.
    """
    sheets: dict[str, list[tuple[int, Path]]] = {}
    for path in sorted(Path(folder).iterdir()):
        if path.suffix.lower() not in MEDIA:
            continue
        m = None if per_page else PAGE.match(path.stem)
        name, page = (m["sheet"], int(m["page"])) if m else (path.stem, 1)
        sheets.setdefault(name, []).append((page, path))
    return {name: [p for _, p in sorted(pages)] for name, pages in sheets.items()}


def parse_sheet(raw: str) -> Sheet:
    """The first JSON object in the model reply, checked against the schema."""
    start, end = raw.find("{"), raw.rfind("}")
    if start < 0 or end < start:
        raise LLMError(f"No JSON object in the reply: {raw[:200]!r}")
    try:
        return Sheet.model_validate(json.loads(raw[start : end + 1]))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise LLMError(f"Unusable sheet JSON: {exc}") from exc


def extract_sheet(name: str, pages: list[Path], client: LLMClient) -> Sheet:
    """Read all pages of one sheet. Retries once if the reply is not valid JSON."""
    if not hasattr(client, "_exe"):
        raise LLMError("Sheet extraction needs the claude_cli backend")
    files = "\n".join(f"Page {i}: {p.resolve()}" for i, p in enumerate(pages, 1))
    user = f"The sheet has {len(pages)} page image(s). Open each one:\n{files}"
    last: LLMError | None = None
    for _ in range(2):
        text, usage = cli_read(pages, client, prompts.system("ocr.sheet"), user)
        with client._lock:
            client.usage.add(usage)
        try:
            sheet = parse_sheet(text)
        except LLMError as exc:
            last = exc
            continue
        sheet.sheet, sheet.pages = name, [p.name for p in pages]
        return sheet
    raise last or LLMError("Sheet extraction failed")


def to_items(sheet: Sheet, dataset: str = "ocr", key: dict[str, str] | None = None) -> list[Item]:
    """Grader items for the sheet. Rough work and questions without marks are skipped."""
    items, seen = [], set()
    for it in sheet.items:
        if it.question_id == "rough" or not it.max_mark or it.max_mark <= 0:
            continue
        qid = f"{sheet.sheet}-{it.question_id}"
        while qid in seen:  # the same number can recur on a sheet that has several parts
            qid += "'"
        seen.add(qid)
        mark = it.teacher_mark
        items.append(
            Item(
                id=qid,
                dataset=dataset,
                question_id=qid,
                question=it.question,
                model_answer=(key or {}).get(it.question_id, ""),
                student_answer=it.student_answer,
                max_mark=it.max_mark,
                human_mark=min(mark, it.max_mark) if mark is not None else None,
            )
        )
    return items


def unsure_spans(sheet: Sheet) -> list[str]:
    """Every span the model was not sure of, from the answers and from the unsure lists."""
    spans = []
    for it in sheet.items:
        spans += it.unsure
        spans += [m.group(1) or "?" for m in UNSURE.finditer(it.student_answer)]
    return spans

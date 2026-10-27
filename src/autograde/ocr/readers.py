"""Choose which model reads a sheet, with fallbacks.

Reading is a separate task from marking, so it has its own model setting (`ocr:` in the config).
The first reader is tried on each sheet or page; if it fails, the next one is tried, so a rate
limit or an outage on a free endpoint does not lose the page. The reader that produced each page
is recorded on the result.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from autograde.config import LLMConfig, ReaderConfig, ReaderRoute
from autograde.llm import LLMClient, LLMError, build_client
from autograde.ocr.hosted import extract_sheet_hosted
from autograde.ocr.sheets import Sheet, extract_sheet

log = logging.getLogger(__name__)


@dataclass
class Reader:
    label: str
    read: Callable[[str, list[Path]], Sheet]
    client: LLMClient | None = None  # set for Claude readers, which report a cost
    hosted: bool = False  # hosted free tiers are rate-limited, so read one page at a time


def build_readers(specs: list[ReaderConfig], effort: str | None = None) -> list[Reader]:
    readers = []
    for spec in specs:
        label = f"{spec.provider}:{spec.model}"
        if spec.provider == "claude_cli":
            client = build_client(LLMConfig(backend="claude_cli", model=spec.model, effort=effort))
            readers.append(Reader(label, lambda n, p, c=client: extract_sheet(n, p, c), client))
        else:
            readers.append(
                Reader(
                    label,
                    lambda n, p, s=spec: extract_sheet_hosted(n, p, s.provider, s.model, s.plain),
                    hosted=True,
                )
            )
    return readers


def read_with_fallback(readers: list[Reader], name: str, pages: list[Path]) -> Sheet | None:
    """The first reader that returns some text, or None if every one fails or reads nothing."""
    for reader in readers:
        try:
            sheet = reader.read(name, pages)
        except LLMError as exc:
            log.warning("%s failed on %s: %s", reader.label, name, str(exc)[:160])
            continue
        if not any(it.student_answer.strip() for it in sheet.items):
            log.warning("%s read nothing on %s", reader.label, name)  # blank is a failed read
            continue
        sheet.reader = reader.label
        return sheet
    log.error("every reader failed on %s", name)
    return None


GERMAN_WORDS = frozenset(
    "der die das und ist nicht ein eine einer mit von zu den dem des im auf für auch sich wird "  # noqa: SIM905
    "werden wurde sind war als bei oder aber wenn dass daß nach über um aus durch wie du "
    "deine sie sprechen spricht und vorname familienname wohnort beruf".split()
)


def classify(sheet: Sheet) -> set[str]:
    """Kinds of text on a page: 'german' (prose with common German words) and 'math'
    (mostly digits, brackets and operators, as in matrices and formulas)."""
    text = " ".join(it.student_answer for it in sheet.items)
    words = re.findall(r"[a-zäöüß]+", text.lower())
    kinds = set()
    if (
        len(words) >= 8
        and sum(w in GERMAN_WORDS or bool(re.search("[äöüß]", w)) for w in words) / len(words)
        >= 0.1
    ):
        kinds.add("german")
    body = re.sub(r"\s", "", text)
    if len(body) >= 20 and len(re.findall(r"[\d\[\](){}=+\-*/^_λ→|\\]", body)) / len(body) >= 0.25:
        kinds.add("math")
    return kinds


def read_routed(
    readers: list[Reader], routes: list[tuple[ReaderRoute, Reader]], name: str, pages: list[Path]
) -> Sheet | None:
    """Read with the main chain, then re-read with the specialist for the kind of text found."""
    sheet = read_with_fallback(readers, name, pages)
    if sheet is None:
        return None
    kinds = classify(sheet)
    for route, reader in routes:
        if route.when in kinds:
            second = read_with_fallback([reader], name, pages)
            if second is not None:
                log.info("%s looks %s, re-read by %s", name, route.when, reader.label)
                return second
    return sheet

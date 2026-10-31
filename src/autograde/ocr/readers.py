"""Choose which model reads a sheet, with fallbacks.

Reading is a separate task from marking, so it has its own model setting (`ocr:` in the config).
The first reader is tried on each sheet or page; if it fails, the next one is tried, so a rate
limit or an outage on a free endpoint does not lose the page. The reader that produced each page
is recorded on the result.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from autograde.config import ReaderConfig, ReaderRoute
from autograde.ocr.hosted import extract_sheet_hosted
from autograde.ocr.sheets import Sheet, unsure_spans

log = logging.getLogger(__name__)


@dataclass
class Reader:
    """A way to read a sheet from page images, with a label."""

    label: str
    read: Callable[[str, list[Path]], Sheet]


def build_readers(specs: list[ReaderConfig]) -> list[Reader]:
    """Build one reader per spec, in order."""
    return [
        Reader(
            f"{spec.provider}:{spec.model}",
            lambda n, p, s=spec: extract_sheet_hosted(n, p, s.provider, s.model, s.plain),
        )
        for spec in specs
    ]


UNSURE_LIMIT = 0.25  # more than this share of words marked unsure: try another reader
REPEAT_LIMIT = 0.4  # one word making up more than this share of a long page: a looping reader


def read_problems(sheet: Sheet) -> list[str]:
    """List why a read should not be trusted.

    The reasons are `empty`, `uncertain` (many unsure words) or `repeating` (the reader got
    stuck in a loop). An empty list means the read can be used.
    """
    words = " ".join(it.student_answer for it in sheet.items).split()
    if not words:
        return ["empty"]
    problems = []
    if len(words) >= 4 and len(unsure_spans(sheet)) / len(words) > UNSURE_LIMIT:
        problems.append("uncertain")
    if (
        len(words) >= 20
        and Counter(w.lower() for w in words).most_common(1)[0][1] / len(words) > REPEAT_LIMIT
    ):
        problems.append("repeating")
    return problems


def read_with_fallback(readers: list[Reader], name: str, pages: list[Path]) -> Sheet | None:
    """Cascade through the readers until one gives a clean read.

    A reader is passed over when it fails for any reason, reads nothing, is unsure of too many
    words, or loops. If no reader is clean, the least doubtful read is kept and marked
    `(degraded)`; None only when every reader failed or read nothing.
    """
    best: tuple[tuple[int, float], Sheet] | None = None
    for reader in readers:
        try:
            sheet = reader.read(name, pages)
        except Exception as exc:  # noqa: BLE001 - whatever went wrong, the next reader gets a go
            log.warning("%s failed on %s: %r", reader.label, name, exc)
            continue
        problems = read_problems(sheet)
        sheet.reader = reader.label
        if not problems:
            return sheet
        log.warning("%s gave a doubtful read of %s: %s", reader.label, name, ", ".join(problems))
        if problems == ["empty"]:  # a blank page is a failed read
            continue
        words = sum(len(it.student_answer.split()) for it in sheet.items)
        doubt = (len(problems), len(unsure_spans(sheet)) / max(words, 1))
        if best is None or doubt < best[0]:
            best = (doubt, sheet)
    if best is not None:
        log.warning("no clean read of %s; keeping %s", name, best[1].reader)
        best[1].reader += " (degraded)"
        return best[1]
    log.error("every reader failed on %s", name)
    return None


GERMAN_WORDS = frozenset(
    "der die das und ist nicht ein eine einer mit von zu den dem des im auf für auch sich wird "  # noqa: SIM905
    "werden wurde sind war als bei oder aber wenn dass daß nach über um aus durch wie du "
    "deine sie sprechen spricht und vorname familienname wohnort beruf".split()
)


INDIC_SHARE = 0.3  # share of letters in an Indic script that makes a page 'indic'
INDIC_BLOCKS = (  # Devanagari to Malayalam, Sinhala excluded; also Ol Chiki and Meetei Mayek
    (0x0900, 0x0DFF),
    (0x1C50, 0x1C7F),
    (0xABC0, 0xABFF),
)


def is_indic(ch: str) -> bool:
    """Say whether a character belongs to an Indian script."""
    return any(lo <= ord(ch) <= hi for lo, hi in INDIC_BLOCKS)


def classify(sheet: Sheet) -> set[str]:
    """Name the kinds of text on a page.

    The kinds are 'german' (prose with common German words), 'math' (mostly digits, brackets
    and operators, as in matrices and formulas) and 'indic' (mostly letters of an Indian
    script, found by Unicode block, so Latin-script pages never match).
    """
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
    letters = [c for c in body if c.isalpha()]
    if len(letters) >= 5 and sum(is_indic(c) for c in letters) / len(letters) >= INDIC_SHARE:
        kinds.add("indic")  # the only kind that is ever sent to the Indic specialist (Bodhan)
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

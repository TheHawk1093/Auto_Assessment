"""Command that reads photographed or scanned answer sheets into text documents for `exam`."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from autograde.cli.common import write_json
from autograde.config import ReaderConfig, Settings
from autograde.intake.files import read_document
from autograde.llm.base import LLMError
from autograde.ocr.answersheet import (
    looks_indic,
    read_answer_sheet,
    unsure_count,
    with_identity,
    word_count,
)
from autograde.ocr.readers import REPEAT_LIMIT, UNSURE_LIMIT
from autograde.ocr.sheets import group_pages

log = logging.getLogger(__name__)


def register(sub) -> None:
    """Add the `scan` command and its flags to the subparsers."""
    p = sub.add_parser(
        "scan", help="read photographed answer sheets into one text document per student"
    )
    p.add_argument("folder", type=Path, help="images named <sheet>_p<page>.png (or one per sheet)")
    p.add_argument("--out", type=Path, required=True, help="folder for the <sheet>.md documents")
    p.add_argument("--paper", type=Path, help="question paper, so the reader knows the numbering")
    p.add_argument("--provider", choices=["openrouter", "bodhan"])
    p.add_argument("--model", help="with --provider; default is the configured reader")
    p.add_argument("--per-page", action="store_true", help="read each image as its own sheet")
    p.add_argument(
        "--identities", type=Path,
        help="JSON {sheet: {student_id, name}} for sheets whose writer is already known "
        "(handed in by a signed-in student); their header is set from it",
    )  # fmt: skip
    p.add_argument(
        "--summary", type=Path, help="where to record what each sheet gave (default: OUT/scan.json)"
    )
    p.set_defaults(func=cmd_scan)


def read_problems(text: str) -> list[str]:
    """List why a read should not be trusted: `uncertain` (many unsure words) or `repeating`.

    An empty list means the text can be used. A reader that returned nothing never gets here: it
    raises an error instead. The limits are the same ones `autograde ocr` uses.
    """
    words = text.split()
    problems = []
    if len(words) >= 4 and unsure_count(text) / len(words) > UNSURE_LIMIT:
        problems.append("uncertain")
    if len(words) >= 20:
        top = max(words.count(w) for w in set(words))
        if top / len(words) > REPEAT_LIMIT:
            problems.append("repeating")
    return problems


def cmd_scan(args: argparse.Namespace, settings: Settings) -> None:
    """Read each sheet once (a sheet already read is kept) and write `<sheet>.md` and scan.json."""
    reader = settings.ocr.reader
    if args.provider:
        if not args.model:
            raise SystemExit("--provider needs --model")
        reader = ReaderConfig(provider=args.provider, model=args.model)
    paper_text = ""
    if args.paper:
        try:
            paper_text = read_document(args.paper)
        except ValueError as exc:
            log.warning("question paper not shown to the reader: %s", exc)
    known = json.loads(args.identities.read_text(encoding="utf-8")) if args.identities else {}
    args.out.mkdir(parents=True, exist_ok=True)
    sheets = group_pages(args.folder, args.per_page)
    if not sheets:
        raise SystemExit(f"no images in {args.folder}")
    summary_path = args.summary or args.out / "scan.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.exists() else {}

    # The main reader (from --provider/--model, else the config) comes first, then the fallbacks
    # from the config, in order. A fallback that is the main reader again is not tried twice.
    chain = [reader]
    for spec in settings.ocr.fallbacks:
        if (spec.provider, spec.model) != (reader.provider, reader.model):
            chain.append(spec)

    def first_read(name: str, pages: list[Path]) -> tuple[str, ReaderConfig, list[str]]:
        """The first reader that gives a clean read: the main one, then the fallbacks in order.

        A reader is passed over when it fails, reads nothing, or reads doubtfully (see
        `read_problems`). If none is clean, the least doubtful read is kept and returned with its
        problems, so the summary can say so.
        """
        error: Exception | None = None
        best: tuple[tuple[int, float], str, ReaderConfig, list[str]] | None = None
        for spec in chain:
            try:
                text = read_answer_sheet(pages, spec.provider, spec.model, paper_text)
            except Exception as exc:  # noqa: BLE001 - try the next reader
                error = exc
                log.warning("%s: reader %s:%s failed: %s", name, spec.provider, spec.model, exc)
                continue
            problems = read_problems(text)
            if not problems:
                return text, spec, []
            log.warning(
                "%s: reader %s:%s read doubtfully (%s); trying the next reader",
                name, spec.provider, spec.model, ", ".join(problems),
            )  # fmt: skip
            doubt = (len(problems), unsure_count(text) / max(len(text.split()), 1))
            if best is None or doubt < best[0]:
                best = (doubt, text, spec, problems)
        if best is not None:
            return best[1], best[2], best[3]
        raise error or LLMError("no reader is configured")

    def indic_reread(
        name: str, pages: list[Path], text: str, used: ReaderConfig
    ) -> tuple[str, ReaderConfig]:
        """Indian-script pages are re-read by the specialist route; on failure keep the text."""
        if not looks_indic(text):
            return text, used
        for route in settings.ocr.routes:
            if route.when != "indic":
                continue
            spec = route.reader
            if (spec.provider, spec.model) == (used.provider, used.model):
                return text, used  # the specialist already read it
            try:
                second = read_answer_sheet(
                    pages, spec.provider, spec.model, paper_text
                )
            except Exception as exc:  # noqa: BLE001 - the first reading stands
                log.warning("%s: Indic re-read failed (%s); keeping the first reading", name, exc)
                return text, used
            log.info("%s looks Indic, re-read by %s:%s", name, spec.provider, spec.model)
            return second, spec
        return text, used

    def read(name: str) -> tuple[str, dict]:
        target = args.out / f"{name}.md"
        if target.exists():  # resume: read by an earlier run, and perhaps corrected since
            return name, summary.get(name, {"status": "kept"})
        pages = sheets[name]
        log.info(
            "reading %s (%d pages) with %s:%s", name, len(pages), reader.provider, reader.model
        )
        used = reader
        try:
            text, used, doubts = first_read(name, pages)
        except Exception as exc:  # noqa: BLE001 - one bad sheet must not lose the others
            log.exception("reading %s failed", name)
            return name, {"status": "failed", "error": str(exc)[:300], "pages": len(pages)}
        text, used = indic_reread(name, pages, text, used)
        who = known.get(name)
        if who:
            text = with_identity(text, who["student_id"], who.get("name", ""))
        target.write_text(text, encoding="utf-8")
        return name, {
            "status": "read", "pages": len(pages), "words": word_count(text),
            "unsure": unsure_count(text), "reader": f"{used.provider}:{used.model}",
            "identity": "known" if who else "from the sheet",
            **({"degraded": doubts} if doubts else {}),
        }  # fmt: skip

    with ThreadPoolExecutor(max_workers=1) as pool:  # one sheet at a time
        for name, info in pool.map(read, sheets):
            summary[name] = info
            print(f"{name}: {info['status']}", {k: v for k, v in info.items() if k != "status"})
    write_json(summary_path, summary)
    failed = [n for n in sheets if summary.get(n, {}).get("status") == "failed"]
    print(f"read {len(sheets) - len(failed)} of {len(sheets)} sheets into {args.out}")
    if failed:
        sys.exit(f"stopped: could not read {', '.join(failed)}. Run again to retry only those.")

"""Command that reads photographed answer sheets into grader items."""

from __future__ import annotations

import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from autograde.config import ReaderConfig, Settings
from autograde.ocr.readers import build_readers, read_routed
from autograde.ocr.sheets import Sheet, group_pages, to_items, unsure_spans

log = logging.getLogger(__name__)


def register(sub) -> None:
    """Add the `ocr` command and its flags to the subparsers."""
    p = sub.add_parser("ocr", help="read photographed answer sheets into items.jsonl")
    p.add_argument("folder", type=Path, help="images named <sheet>_p<page>.jpeg")
    p.add_argument("--out", type=Path, required=True, help="folder to write the results to")
    p.add_argument(
        "--model",
        help="override the configured reader with this model (needs --provider)",
    )
    p.add_argument(
        "--provider", choices=["openrouter", "bodhan"],
        help="override the configured reader: a hosted model (needs --model; keys in .env)",
    )  # fmt: skip
    p.add_argument("--plain", action="store_true", help="hosted models: plain transcription only")
    p.add_argument("--per-page", action="store_true", help="read each image as its own sheet")
    p.add_argument("--key", type=Path, help="JSON {sheet: {question_id: model answer}}")
    p.set_defaults(func=cmd_ocr)


def cmd_ocr(args: argparse.Namespace, settings: Settings) -> None:
    """Read photographed answer sheets into items and write them to the output folder."""
    if args.provider and not args.model:
        raise SystemExit("--provider needs --model")
    if args.provider or args.model:  # flags override the configured reader and fallbacks
        spec = ReaderConfig(provider=args.provider, model=args.model, plain=args.plain)
        specs, routes = [spec], []
    else:
        specs, routes = [settings.ocr.reader, *settings.ocr.fallbacks], settings.ocr.routes
    readers = build_readers(specs)
    special = build_readers([r.reader for r in routes])
    pairs = list(zip(routes, special, strict=True))
    keys = json.loads(args.key.read_text(encoding="utf-8")) if args.key else {}
    args.out.mkdir(parents=True, exist_ok=True)
    sheets = group_pages(args.folder, args.per_page)

    def read(name: str):
        saved = args.out / f"{name}.sheet.json"
        if saved.exists():  # resume: this sheet was read by an earlier run
            return Sheet.model_validate_json(saved.read_text(encoding="utf-8"))
        log.info("reading %s (%d pages)", name, len(sheets[name]))
        try:
            sheet = read_routed(readers, pairs, name, sheets[name])
        except Exception:  # noqa: BLE001 - one bad page must not lose the others
            log.exception("reading %s failed", name)
            return None
        if sheet is not None:  # saved at once, so a crash later loses nothing
            saved.write_text(sheet.model_dump_json(indent=2), encoding="utf-8")
        return sheet

    # free tiers are rate-limited, so hosted models are read one page at a time
    workers = 1 if any(r.hosted for r in readers + special) else min(len(sheets), 4)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        results = [r for r in pool.map(read, sheets) if r is not None]
    lines = []
    for sheet in results:
        (args.out / f"{sheet.sheet}.sheet.json").write_text(
            sheet.model_dump_json(indent=2), encoding="utf-8"
        )
        items = to_items(sheet, key=keys.get(sheet.sheet))
        lines += [it.model_dump_json() for it in items]
        print(f"{sheet.sheet}: {len(items)} items, {len(unsure_spans(sheet))} unsure spans, "
              f"read by {sheet.reader}")  # fmt: skip
    (args.out / "items.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    done = f"{len(results)}/{len(sheets)} sheets"
    print(f"wrote {args.out / 'items.jsonl'}  ({done})")

"""Command that reads photographed answer sheets into grader items."""

from __future__ import annotations

import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from autograde.cli.common import write_json
from autograde.config import Settings
from autograde.llm import build_client
from autograde.ocr.sheets import extract_sheet, group_pages, to_items, unsure_spans

log = logging.getLogger(__name__)


def register(sub) -> None:
    p = sub.add_parser("ocr", help="read photographed answer sheets into items.jsonl")
    p.add_argument("folder", type=Path, help="images named <sheet>_p<page>.jpeg")
    p.add_argument("--out", type=Path, required=True, help="folder to write the results to")
    p.add_argument("--model", help="override the model in the config")
    p.add_argument("--effort", help="override the effort in the config")
    p.add_argument("--key", type=Path, help="JSON {sheet: {question_id: model answer}}")
    p.set_defaults(func=cmd_ocr)


def cmd_ocr(args: argparse.Namespace, settings: Settings) -> None:
    cfg = settings.llm.model_copy(
        update={k: v for k, v in {"model": args.model, "effort": args.effort}.items() if v}
    )
    client = build_client(cfg)
    keys = json.loads(args.key.read_text(encoding="utf-8")) if args.key else {}
    args.out.mkdir(parents=True, exist_ok=True)
    sheets = group_pages(args.folder)

    def read(name: str):
        log.info("reading %s (%d pages)", name, len(sheets[name]))
        return extract_sheet(name, sheets[name], client)

    with ThreadPoolExecutor(max_workers=len(sheets)) as pool:
        results = list(pool.map(read, sheets))
    lines = []
    for sheet in results:
        (args.out / f"{sheet.sheet}.sheet.json").write_text(
            sheet.model_dump_json(indent=2), encoding="utf-8"
        )
        items = to_items(sheet, key=keys.get(sheet.sheet))
        lines += [it.model_dump_json() for it in items]
        print(f"{sheet.sheet}: {len(items)} items, {len(unsure_spans(sheet))} unsure spans")
    (args.out / "items.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(args.out / "usage.json", client.usage.as_dict())
    print(f"wrote {args.out / 'items.jsonl'}  cost ${client.usage.cost_usd:.3f}")

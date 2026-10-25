"""Grade the same sheets from different OCR sources and compare the marks.

    python tools/ocr_pipeline_eval.py --source sonnet=runs/ocrp_sonnet --source tess=runs/ocrb_tess

Every source goes through the same steps: its text for each sheet is matched to the questions in
data/OCR_Dataset/key.json by a text-only model, then the existing pipeline marks each answer with
the same reference key. A "truth" source (the student's answers as read by hand) is always added:
it is the best any OCR could do, so the gap to it is the marking error caused by OCR alone.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.config import load_settings
from autograde.llm import build_client
from autograde.ocr.sheets import Sheet
from autograde.pipeline.run import run_items
from autograde.schemas import Item

ROOT = Path(__file__).resolve().parent.parent
KEY = json.loads((ROOT / "data/OCR_Dataset/key.json").read_text("utf-8"))
log = logging.getLogger("ocr_eval")


class Assigned(BaseModel):
    class Entry(BaseModel):
        id: str
        text: str

    answers: list[Entry]


def sheet_text(folder: Path, sheet: str) -> str:
    """All text a source produced for the pages of one sheet, pages in order."""
    parts = []
    lines_file = folder / "lines.json"
    if lines_file.exists():
        lines = json.loads(lines_file.read_text("utf-8"))
        for name in sorted(k for k in lines if k.startswith(sheet + "_p")):
            parts.append("\n".join(lines[name]))
    else:
        for path in sorted(folder.glob(f"{sheet}_p*.sheet.json")):
            parts.append(
                "\n".join(
                    i.student_answer
                    for i in Sheet.model_validate_json(path.read_text("utf-8")).items
                )
            )
    return "\n".join(parts)


def assign(client, sheet: str, text: str) -> dict[str, str]:
    items = KEY[sheet]["items"]
    questions = "\n".join(f"[{it['id']}] {it['question']}" for it in items)
    user = f"Questions:\n{questions}\n\nOCR text of the sheet:\n{text}"
    got = client.ask(prompts.system("ocr.assign"), user, Assigned)
    found = {e.id: e.text for e in got.answers}
    return {it["id"]: found.get(it["id"], "") for it in items}


def build_items(source: str, answers: dict[str, dict[str, str]]) -> list[Item]:
    out = []
    for sheet, answered in answers.items():
        for it in KEY[sheet]["items"]:
            qid = f"{sheet}-{it['id']}"
            out.append(
                Item(
                    id=f"{source}:{qid}", dataset="ocrset", question_id=qid,
                    question=it["question"], model_answer=it["model_answer"],
                    student_answer=answered[it["id"]], max_mark=it["max_mark"],
                )
            )  # fmt: skip
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--source", action="append", default=[], metavar="NAME=FOLDER")
    p.add_argument("--config", default=str(ROOT / "configs/poc.yaml"))
    p.add_argument("--out", default="runs/ocr_eval")
    p.add_argument("--assign-model", default="haiku")
    a = p.parse_args()
    logging.basicConfig(level=logging.WARNING)

    settings = load_settings(Path(a.config))
    out = ROOT / a.out
    settings.paths.rubrics_dir = out / "rubrics"
    client = build_client(settings.llm)
    assigner = build_client(settings.llm.model_copy(update={"model": a.assign_model}))

    sources: dict[str, list[Item]] = {
        "truth": build_items(
            "truth",
            {
                s: {i["id"]: i["student_truth"] for i in KEY[s]["items"]}
                for s in KEY
                if not s.startswith("_")
            },
        )
    }
    cache = out / "assigned.json"
    done = json.loads(cache.read_text("utf-8")) if cache.exists() else {}
    for spec in a.source:
        name, folder = spec.split("=", 1)
        if name not in done:
            done[name] = {
                s: assign(assigner, s, sheet_text(ROOT / folder, s))
                for s in KEY
                if not s.startswith("_")
            }
            out.mkdir(parents=True, exist_ok=True)
            cache.write_text(json.dumps(done, ensure_ascii=False, indent=1), "utf-8")
        sources[name] = build_items(name, done[name])

    results = {}
    for name, items in sources.items():
        res = run_items(items, "pipeline", client, settings, out / f"{name}.jsonl")
        results[name] = {r.item.question_id: r.predicted_mark for r in res}
    truth = results["truth"]

    clean = {"Probab": {"2", "4", "5", "6"}, "German": {"1", "3", "4"}}
    print(f"{'source':<22}{'item MAE vs perfect':>20}{'same mark':>11}{'total MAE vs teacher':>22}")
    for name, marks in results.items():
        diffs = [abs(marks[q] - truth[q]) for q in truth]
        errs = []
        for sheet, groups in clean.items():
            for g in groups:
                ids = [
                    q
                    for q in marks
                    if q.startswith(f"{sheet}-{g}") and re.fullmatch(rf"{sheet}-{g}[a-z]?", q)
                ]
                errs.append(abs(sum(marks[q] for q in ids) - KEY[sheet]["teacher_totals"][g]))
        same = sum(d < 1e-6 for d in diffs) / len(diffs)
        print(
            f"{name:<22}{sum(diffs) / len(diffs):>20.3f}{same:>11.0%}{sum(errs) / len(errs):>22.3f}"
        )
    print(f"cost: grading ${client.usage.cost_usd:.3f}, assignment ${assigner.usage.cost_usd:.3f}")
    (out / "summary.json").write_text(json.dumps(results, indent=1), "utf-8")


if __name__ == "__main__":
    main()

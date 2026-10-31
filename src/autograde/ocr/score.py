"""Score OCR output against a hand-made truth file.

    python -m autograde.ocr.score data/OCR_Dataset/truth.json runs/ocr_haiku runs/ocr_rapid ...

A folder holds either `<sheet>.sheet.json` files (model extraction) or `lines.json` (plain OCR
text lines per image). Three scores per sheet, where the truth file has the data for them:
- token recall: share of the student's own words and numbers that appear in the output,
- facts: share of listed key strings (formulas, matrices, conclusions) found, ignoring spaces,
- totals: share of the teacher's per-question totals that were read correctly.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from autograde.ocr.metrics import facts, precision, recall
from autograde.ocr.sheets import Sheet


def totals(sheet: Sheet) -> dict[str, float]:
    """Return the teacher's mark per whole question on a sheet."""
    got = dict(sheet.teacher_totals)
    for it in sheet.items:
        root = re.match(r"\d+", it.question_id)
        if it.teacher_mark is not None and root and root[0] not in got:
            got[root[0]] = it.teacher_mark
    return got


def score(truth: dict, folder: Path) -> dict[str, dict[str, float | None]]:
    """Per truth entry (sheet or page): recall, fuzzy recall, precision, facts, totals."""
    rows: dict[str, dict[str, float | None]] = {}
    lines_file = folder / "lines.json"
    lines = json.loads(lines_file.read_text("utf-8")) if lines_file.exists() else None
    for name, t in truth.items():
        if name.startswith("_"):
            continue
        sheet = None
        if lines is not None:
            text = " ".join(lines.get(f"{name}.jpeg", []))
        else:
            path = folder / f"{name}.sheet.json"
            if not path.exists():
                continue
            sheet = Sheet.model_validate_json(path.read_text("utf-8"))
            text = " ".join(i.student_answer for i in sheet.items)
        want = t.get("teacher_totals")
        row: dict[str, float | None] = {
            "recall": recall(t["tokens"], text) if "tokens" in t else None,
            "fuzzy": recall(t["tokens"], text, fuzzy=True) if "tokens" in t else None,
            "precision": precision(t["tokens"], text)
            if "tokens" in t and t.get("precision", True)
            else None,
            "facts": facts(t["facts"] if "facts" in t else t["must_contain"], text)
            if ("facts" in t or "must_contain" in t)
            else None,
            "totals": None,
        }
        if want and sheet:
            got = totals(sheet)
            row["totals"] = sum(got.get(k) == v for k, v in want.items()) / len(want)
        rows[name] = row
    return rows


def main(argv: list[str]) -> None:
    """Print a score table for each folder of readings against the truth file."""
    truth = json.loads(Path(argv[0]).read_text("utf-8"))
    fmt = lambda v: "  -  " if v is None else f"{v:5.0%}"  # noqa: E731
    print(f"{'run':<22}{'entry':<22}{'recall':>7}{'fuzzy':>7}{'prec':>7}{'facts':>7}{'totals':>7}")
    for folder in argv[1:]:
        for entry, r in score(truth, Path(folder)).items():
            print(
                f"{Path(folder).name:<22}{entry:<22}{fmt(r['recall']):>7}{fmt(r['fuzzy']):>7}"
                f"{fmt(r['precision']):>7}{fmt(r['facts']):>7}{fmt(r['totals']):>7}"
            )


if __name__ == "__main__":
    main(sys.argv[1:])

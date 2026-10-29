"""Score how well a reader identifies Indic handwriting: character and word error rates.

    python tools/ocr/indic_ocr_eval.py --truth data/raw/indic_words/truth_tune.json \
        --source gemini=runs/indic_tune_gemini --source sonnet=runs/indic_tune_sonnet

`--source` is the output folder of `autograde ocr --per-page` (one `<page>_p1.sheet.json` each).
The error rate counts a base letter with its vowel signs, and a conjunct joined by a virama, as
one unit (a grapheme cluster), so combining marks are not charged as separate errors. Text is
Unicode-normalised (NFC) and spaces are ignored for the character rate. No grading happens here:
this is the reading step alone.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

UNSURE = re.compile(r"\[\?(.*?)\?\]")


def clusters(text: str) -> list[str]:
    """Grapheme-like units: a base with its marks, joiners, and virama-joined conjuncts."""
    out: list[str] = []
    attach_next = False
    for ch in unicodedata.normalize("NFC", re.sub(r"\s+", "", text)):
        if out and (unicodedata.category(ch).startswith("M") or ch in "‌‍" or attach_next):
            out[-1] += ch
        else:
            out.append(ch)
        attach_next = unicodedata.combining(ch) == 9  # a virama pulls in the next letter
    return out


def distance(a: list, b: list) -> int:
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def page_text(folder: Path, name: str) -> str:
    path = folder / f"{name}_p1.sheet.json"
    if not path.exists():
        return ""
    sheet = json.loads(path.read_text(encoding="utf-8"))
    text = " ".join(it.get("student_answer", "") for it in sheet.get("items", []))
    return UNSURE.sub(r"\1", text)


def score(truth: dict[str, str], folder: Path) -> dict:
    per_lang: dict[str, list[float]] = {}
    for name, ref in truth.items():
        hyp = page_text(folder, name)
        r, h = clusters(ref), clusters(hyp)
        w_r, w_h = ref.split(), hyp.split()
        row = per_lang.setdefault(name.split("_", 1)[0], [0, 0, 0, 0, 0, 0])
        row[0] += distance(r, h)
        row[1] += len(r)
        row[2] += distance(w_r, w_h)
        row[3] += len(w_r)
        row[4] += not hyp.strip()
        row[5] += 1
    out = {}
    for lang, (ce, cn, we, wn, empty, pages) in per_lang.items():
        out[lang] = {
            "pages": pages,
            "empty": empty,
            "cer": round(ce / max(cn, 1), 3),
            "wer": round(we / max(wn, 1), 3),
        }
    tot = [sum(v[i] for v in per_lang.values()) for i in range(6)]
    out["all"] = {
        "pages": tot[5],
        "empty": tot[4],
        "cer": round(tot[0] / max(tot[1], 1), 3),
        "wer": round(tot[2] / max(tot[3], 1), 3),
    }
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--truth", type=Path, required=True)
    p.add_argument("--source", action="append", default=[], metavar="NAME=FOLDER")
    a = p.parse_args()
    truth = json.loads(a.truth.read_text(encoding="utf-8"))
    for spec in a.source:
        name, folder = spec.split("=", 1)
        res = score(truth, Path(folder))
        line = "  ".join(
            f"{k}: CER {v['cer']:.3f} WER {v['wer']:.3f} (empty {v['empty']})"
            for k, v in res.items()
        )
        print(f"{name:<14}{line}")


if __name__ == "__main__":
    main()

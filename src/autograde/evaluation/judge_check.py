"""Is the feedback judge right? A sheet for a person who reads the language, and the agreement.

`export_sheet` writes feedback from finished runs next to the judge's yes/no answers, with empty
columns for a human to fill (y or n, same questions). `agreement` then compares the two per
question: raw agreement and Cohen's kappa. The judge is a model reading Indic text that nobody has
yet checked, so this is the test that says how far its pass rates can be trusted.
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path

CRITERIA = (
    "anchored",
    "names_missed_point",
    "explains_why",
    "actionable",
    "correct",
    "consistent_with_marks",
)
HUMAN = "human_"
SHEET_FIELDS = [
    "run",
    "id",
    "question",
    "model_answer",
    "student_answer",
    "marks",
    "feedback",
    *CRITERIA,
    *(HUMAN + c for c in CRITERIA),
]


def _lines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _mark(value: object) -> str:
    return {True: "y", False: "n"}.get(value, "") if value is not None else ""


def export_sheet(runs_dir: Path, names: list[str], per_run: int, seed: int = 0) -> list[dict]:
    """Pick up to `per_run` judged answers from each run for a person to rate.

    Answers are picked by a hash of the answer id (not by how they scored), so runs on the
    same answers give the same ones and variants can be compared. The rows are shuffled, so
    a rater sees the variants mixed.
    """
    rows = []
    for name in names:
        judged = {x["id"]: x for x in _lines(runs_dir / name / "feedback_judgements.jsonl")}
        results = [
            r for r in _lines(runs_dir / name / "results.jsonl") if r["item"]["id"] in judged
        ]
        results.sort(key=lambda r: hashlib.sha1(f"{seed}{r['item']['id']}".encode()).hexdigest())
        for r in results[:per_run]:
            item, fb = r["item"], r["feedback"] or {}
            rows.append(
                {
                    "run": name,
                    "id": item["id"],
                    "question": item["question"],
                    "model_answer": item["model_answer"],
                    "student_answer": item["student_answer"],
                    "marks": f"{r['predicted_mark']:g} / {item['max_mark']:g}",
                    "feedback": _feedback_text(fb),
                    **{c: _mark(judged[item["id"]].get(c)) for c in CRITERIA},
                    **{HUMAN + c: "" for c in CRITERIA},
                }
            )
    random.Random(seed).shuffle(rows)
    return rows


def _feedback_text(fb: dict) -> str:
    from autograde.schemas import Feedback

    return Feedback.model_validate(fb).text() if fb else ""


def write_sheet(rows: list[dict], path: Path) -> None:
    """Write the rating sheet as a CSV that Excel opens correctly."""
    with path.open("w", encoding="utf-8-sig", newline="") as f:  # BOM: Excel reads Indic text
        writer = csv.DictWriter(f, fieldnames=SHEET_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def cohen_kappa(pairs: list[tuple[bool, bool]]) -> float | None:
    """Return Cohen's kappa for pairs of (judge, person) ratings.

    Returns None when there are no pairs, or when chance agreement is already total.
    """
    n = len(pairs)
    if not n:
        return None
    observed = sum(a == b for a, b in pairs) / n
    pa = sum(a for a, _ in pairs) / n
    pb = sum(b for _, b in pairs) / n
    expected = pa * pb + (1 - pa) * (1 - pb)
    return None if expected >= 1 else round((observed - expected) / (1 - expected), 3)


def agreement(path: Path) -> dict[str, dict]:
    """Compare a person's ratings with the judge's, per question.

    Reports how many answers the person filled, how often they agree with the judge, and
    kappa. Rows the person left blank for a question are skipped.
    """
    with path.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for c in CRITERIA:
        pairs = [
            (r[c] == "y", r[HUMAN + c].strip().lower() == "y")
            for r in rows
            if r[c] in ("y", "n") and r[HUMAN + c].strip().lower() in ("y", "n")
        ]
        out[c] = {
            "n": len(pairs),
            "agree": round(sum(a == b for a, b in pairs) / len(pairs), 3) if pairs else None,
            "kappa": cohen_kappa(pairs),
            "judge_yes": round(sum(a for a, _ in pairs) / len(pairs), 3) if pairs else None,
            "human_yes": round(sum(b for _, b in pairs) / len(pairs), 3) if pairs else None,
        }
    return out

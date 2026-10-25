"""Fit the dataset-specific settings from a few teacher-marked answers, with no model calls.

Which settings depend on the teacher and cannot be known from the questions alone:
how much a "partial" is worth, and whether the grader is overall too hard or too easy.
Both can be fitted from verdicts that are already saved, so a teacher only has to mark a
small set of answers once.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from autograde.evaluation.metrics import summarise
from autograde.pipeline.rescore import rescore
from autograde.schemas import Result, Rubric

PARTIAL_GRID = (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
STRETCH_GRID = (0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.5)  # multiplies every mark, capped at the total
MIN_TRUSTED = 20  # fewer marked answers than this: report, but do not trust the fit


def _stretch(results: Sequence[Result], k: float) -> list[Result]:
    return [
        r.model_copy(update={"predicted_mark": min(r.item.max_mark, r.predicted_mark * k)})
        for r in results
    ]


def form_gate_report(results: Sequence[Result]) -> dict:
    """How often the form gate cut marks, and whether the teacher agreed it should."""
    capped = [r for r in results if "keyword_list_capped" in r.flags and r.item.human_mark]
    wrong = [r for r in capped if r.item.human_mark / r.item.max_mark > 0.5]
    return {"capped": len(capped), "teacher_gave_more_than_half": len(wrong)}


def calibrate(results: Sequence[Result], rubrics: Mapping[str, Rubric]) -> dict:
    """Error and bias for each partial weight, then the best partial weight and stretch."""
    marked = [r for r in results if r.item.human_mark is not None and r.grading is not None]
    if not marked:
        return {"n": 0}
    table = {}
    for pw in PARTIAL_GRID:
        s = summarise(rescore(marked, rubrics, pw))
        table[pw] = {"error": round(s["mean_abs_error"], 3), "bias": round(s["bias"], 3)}
    best_pw = min(table, key=lambda w: (table[w]["error"], abs(table[w]["bias"])))
    priced = rescore(marked, rubrics, best_pw)
    stretch = {k: round(summarise(_stretch(priced, k))["mean_abs_error"], 3) for k in STRETCH_GRID}
    best_k = min(stretch, key=lambda k: (stretch[k], abs(k - 1)))
    return {
        "n": len(marked),
        "trusted": len(marked) >= MIN_TRUSTED,
        "by_partial_weight": table,
        "best_partial_weight": best_pw,
        "by_stretch": stretch,
        "best_stretch": best_k,
        "form_gate": form_gate_report(marked),
    }

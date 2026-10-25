"""Criterion-level agreement: does the grader tick the same rubric criteria as the teacher?

Needs items that carry the teacher's per-criterion labels (RiceChem). Each criterion is met,
partly met or not met; "credit" means met or partly met.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence

from autograde.schemas import Result


def _scores(tp: int, fp: int, fn: int, tn: int) -> dict:
    total = tp + fp + fn + tn
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {
        "n": total,
        "accuracy": round((tp + tn) / total, 3) if total else 0.0,
        "precision": round(prec, 3),
        "recall": round(rec, 3),
        "f1": round(f1, 3),
    }


def criteria_report(results: Sequence[Result]) -> dict:
    """Agreement on credit (met or partial) per criterion, and exact agreement on the status."""
    counts: dict[str, list[int]] = defaultdict(lambda: [0, 0, 0, 0])  # tp fp fn tn
    exact = total = 0
    for r in results:
        if not r.grading or not r.item.labels:
            continue
        for v in r.grading.verdicts:
            truth = r.item.labels.get(v.point_id)
            if truth is None:
                continue
            total += 1
            exact += v.status == truth
            got, want = v.status != "not_met", truth != "not_met"
            c = counts[v.point_id]
            c[0 if got and want else 1 if got else 2 if want else 3] += 1
    if not total:
        return {"n": 0}
    ded = [0, 0, 0, 0]
    for r in results:
        truth = r.item.labels.get("D1") if r.grading else None
        if truth is not None:
            got, want = bool(r.grading.deductions), truth == "met"
            ded[0 if got and want else 1 if got else 2 if want else 3] += 1
    allc = [sum(c[i] for c in counts.values()) for i in range(4)]
    return {
        "criteria_judged": total,
        "exact_status_agreement": round(exact / total, 3),
        "credit": _scores(*allc),
        "by_point": {p: _scores(*c) for p, c in sorted(counts.items())},
        "deductions": _scores(*ded),
    }

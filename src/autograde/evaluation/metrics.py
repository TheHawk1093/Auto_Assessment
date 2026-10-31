"""Compare predicted marks with the teacher's marks. Pure functions, no model calls.

All scores are put on the same footing by dividing by the question's total marks, then
cutting into five levels (0 to 4) for the agreement counts.
"""

from __future__ import annotations

import math
from collections.abc import Sequence

from autograde.schemas import Result

LEVELS = 4


def level(mark: float, max_mark: float) -> int:
    """Round a mark to one of the discrete grade levels from 0 to LEVELS."""
    return min(LEVELS, max(0, round(LEVELS * mark / max_mark)))


def pearson(xs: Sequence[float], ys: Sequence[float]) -> float | None:
    """Return the Pearson correlation, or None if there are under two points or no spread."""
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys, strict=True)) / (sx * sy)


def quadratic_weighted_kappa(a: Sequence[int], b: Sequence[int]) -> float | None:
    """Agreement between two sets of levels, penalising bigger gaps more. 1 is perfect."""
    n = len(a)
    if n == 0:
        return None
    k = LEVELS + 1
    obs = [[0.0] * k for _ in range(k)]
    for x, y in zip(a, b, strict=True):
        obs[x][y] += 1
    ha = [sum(row) for row in obs]
    hb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    num = den = 0.0
    for i in range(k):
        for j in range(k):
            w = (i - j) ** 2 / (k - 1) ** 2
            num += w * obs[i][j]
            den += w * ha[i] * hb[j] / n
    return None if den == 0 else 1 - num / den


def summarise(results: Sequence[Result]) -> dict[str, float | int | None]:
    """Score predicted marks against the teacher's marks.

    Results without a teacher mark are ignored. Marks are compared as shares of the maximum.
    """
    rows = [(r.predicted_mark, r.item.human_mark, r.item.max_mark) for r in results
            if r.item.human_mark is not None]  # fmt: skip
    if not rows:
        return {"n": 0}
    pred_n = [p / m for p, _, m in rows]
    human_n = [h / m for _, h, m in rows]
    diffs = [p - h for p, h in zip(pred_n, human_n, strict=True)]
    lv_pred = [level(p, m) for p, _, m in rows]
    lv_human = [level(h, m) for _, h, m in rows]
    return {
        "n": len(rows),
        "mean_abs_error": sum(abs(d) for d in diffs) / len(diffs),  # share of total marks
        "bias": sum(diffs) / len(diffs),  # >0 means the grader is more generous than the teacher
        "same_level": sum(a == b for a, b in zip(lv_pred, lv_human, strict=True)) / len(rows),
        "within_one_level": sum(abs(a - b) <= 1 for a, b in zip(lv_pred, lv_human, strict=True))
        / len(rows),
        "qwk": quadratic_weighted_kappa(lv_pred, lv_human),
        "pearson": pearson(pred_n, human_n),
    }


def band(result: Result) -> str:
    """Quality band by the teacher's mark, because middle answers are the hardest to mark."""
    share = (result.item.human_mark or 0.0) / result.item.max_mark
    return "low" if share < 1 / 3 else "mid" if share < 2 / 3 else "high"


def report(results: Sequence[Result]) -> dict[str, object]:
    """Build the full metrics report for a run.

    Returns the overall summary, a summary per teacher-mark band, and the share of results
    that carry flags.
    """
    graded = [r for r in results if r.item.human_mark is not None]
    out: dict[str, object] = {"overall": summarise(graded)}
    out["by_band"] = {
        b: summarise([r for r in graded if band(r) == b]) for b in ("low", "mid", "high")
    }
    out["flagged_share"] = sum(bool(r.flags) for r in results) / len(results) if results else 0.0
    return out

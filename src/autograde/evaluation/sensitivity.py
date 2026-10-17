"""Compare two runs on the same answers: how much did the marks move, and did accuracy change?"""

from __future__ import annotations

from collections.abc import Sequence

from autograde.schemas import Result


def compare_runs(a: Sequence[Result], b: Sequence[Result]) -> dict:
    """Run b is usually a changed copy of run a (for example masked model answers)."""
    by_id = {r.item.id: r for r in b}
    pairs = [(r, by_id[r.item.id]) for r in a if r.item.id in by_id]
    if not pairs:
        return {"n": 0}

    def mean(xs: Sequence[float]) -> float:
        return sum(xs) / len(xs)

    moves = [abs(x.predicted_mark - y.predicted_mark) / x.item.max_mark for x, y in pairs]
    err_a = [abs(x.predicted_mark - x.item.human_mark) / x.item.max_mark for x, _ in pairs]
    err_b = [abs(y.predicted_mark - y.item.human_mark) / y.item.max_mark for _, y in pairs]
    return {
        "n": len(pairs),
        "mean_mark_change": round(mean(moves), 4),
        "share_moved_over_10pct": round(sum(m > 0.1 for m in moves) / len(moves), 3),
        "error_a": round(mean(err_a), 4),
        "error_b": round(mean(err_b), 4),
        "error_change": round(mean(err_b) - mean(err_a), 4),
    }

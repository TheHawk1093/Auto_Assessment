"""How steady is the grader, and does voting help? Needs a run made with votes > 1."""

from __future__ import annotations

from collections.abc import Sequence

from autograde.schemas import Result


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def vote_report(results: Sequence[Result]) -> dict:
    """Error of each single vote against the teacher, error of the combined vote, and spread."""
    rows = [r for r in results if len(r.votes) > 1]
    if not rows:
        return {"n": 0}
    k = min(len(r.votes) for r in rows)
    single = [
        _mean([abs(r.votes[i] - r.item.human_mark) / r.item.max_mark for r in rows])
        for i in range(k)
    ]
    spread = [(max(r.votes) - min(r.votes)) / r.item.max_mark for r in rows]
    voted = _mean([abs(r.predicted_mark - r.item.human_mark) / r.item.max_mark for r in rows])
    return {
        "n": len(rows),
        "votes": k,
        "error_each_vote": [round(x, 4) for x in single],
        "error_single_avg": round(_mean(single), 4),
        "error_voted": round(voted, 4),
        "mean_spread": round(_mean(spread), 4),
        "share_votes_all_agree": round(sum(s < 1e-9 for s in spread) / len(rows), 3),
        "share_with_split_point": round(
            sum(any(f.startswith("vote_split") for f in r.flags) for r in rows) / len(rows), 3
        ),
    }


def review_report(results: Sequence[Result]) -> dict:
    """Does the second model's disagreement point at the answers the grader gets wrong?"""
    rows = [r for r in results if r.second_mark is not None]
    if not rows:
        return {"n": 0}

    def err(r: Result) -> float:
        return abs(r.predicted_mark - r.item.human_mark) / r.item.max_mark

    flagged = [r for r in rows if "models_disagree" in r.flags]
    agreed = [r for r in rows if "models_disagree" not in r.flags]
    return {
        "n": len(rows),
        "share_flagged": round(len(flagged) / len(rows), 3),
        "error_when_models_agree": round(_mean([err(r) for r in agreed]), 4),
        "error_when_flagged": round(_mean([err(r) for r in flagged]), 4),
    }

"""Do marks and feedback move with the rubric's strictness?

The same answers are marked under a lenient, a moderate and a harsh rubric. If the grader
follows the rubric, marks fall as the rubric gets harsher, and the feedback names more gaps.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from autograde.pipeline.levels import LEVELS
from autograde.schemas import Result


def _mean(xs: Sequence[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _feedback_words(r: Result) -> int:
    fb = r.feedback
    if fb is None:
        return 0
    parts = [*fb.strengths, fb.summary]
    for x in fb.improvements:
        parts += [x.issue, x.why, x.fix]
    return sum(len(p.split()) for p in parts)


def level_summary(results: Sequence[Result]) -> dict:
    """One level: average mark, gap to the teacher, and how much feedback was written."""
    share = [r.predicted_mark / r.item.max_mark for r in results]
    gap = [(r.predicted_mark - r.item.human_mark) / r.item.max_mark for r in results]
    return {
        "n": len(results),
        "mean_mark_share": round(_mean(share), 4),
        "teacher_mean_share": round(
            _mean([r.item.human_mark / r.item.max_mark for r in results]), 4
        ),
        "error": round(_mean([abs(g) for g in gap]), 4),
        "bias": round(_mean(gap), 4),
        "improvements_per_answer": round(
            _mean([len(r.feedback.improvements) if r.feedback else 0 for r in results]), 2
        ),
        "feedback_words": round(_mean([_feedback_words(r) for r in results]), 1),
    }


def compliance(runs: Mapping[str, Sequence[Result]]) -> dict:
    """runs: level name -> results of the same answers. Returns per-level and ordering stats."""
    levels = [lv for lv in LEVELS if lv in runs]
    by_level = {lv: {r.item.id: r for r in runs[lv]} for lv in levels}
    common = set.intersection(*(set(d) for d in by_level.values())) if levels else set()
    out: dict = {"levels": {lv: level_summary(list(by_level[lv].values())) for lv in levels}}
    if len(levels) < 2 or not common:
        return out
    ids = sorted(common)
    marks = {lv: [by_level[lv][i].predicted_mark for i in ids] for lv in levels}
    ordered = sum(
        all(marks[a][k] >= marks[b][k] - 1e-9 for a, b in zip(levels, levels[1:], strict=False))
        for k in range(len(ids))
    )
    strict = sum(
        all(marks[a][k] > marks[b][k] + 1e-9 for a, b in zip(levels, levels[1:], strict=False))
        for k in range(len(ids))
    )
    first, last = levels[0], levels[-1]
    spread = [
        (marks[first][k] - marks[last][k]) / by_level[first][ids[k]].item.max_mark
        for k in range(len(ids))
    ]
    out["ordering"] = {
        "answers": len(ids),
        "share_never_rising_with_strictness": round(ordered / len(ids), 3),
        "share_strictly_falling": round(strict / len(ids), 3),
        "mean_lenient_minus_harsh": round(_mean(spread), 4),
    }
    return out

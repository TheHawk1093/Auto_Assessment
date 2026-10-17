"""Best-of-N marking: mark the same answer several times, then combine the verdicts per point.

The model decides each verdict; code takes the majority and prices it. Points where the
markers disagree are reported, so a split vote shows where the grader is unsure.
Use an odd number of votes: with an even number a tie falls to the stricter middle verdict.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Sequence

from autograde.pipeline.verify import apply_mark_rule, evidence_in_answer
from autograde.schemas import Grading, PointVerdict, Rubric

_STATUSES = ("not_met", "partial", "met")  # ordered from least to most credit


def models_disagree(first: float, second: float, max_mark: float, gap: float) -> bool:
    """True when two models' marks differ by more than `gap` of the total marks."""
    return abs(first - second) / max_mark > gap + 1e-9


def combine(
    gradings: Sequence[Grading], rubric: Rubric, answer: str, partial_weight: float
) -> tuple[Grading, list[str]]:
    """The majority verdict for each point, priced by the mark rule, and the split point ids."""
    out: list[PointVerdict] = []
    split: list[str] = []
    for point in rubric.points:
        votes = [next((v for v in g.verdicts if v.point_id == point.id), None) for g in gradings]
        statuses = [v.status if v else "not_met" for v in votes]
        counts = Counter(statuses)
        top = max(counts.values())
        tied = [s for s, c in counts.items() if c == top]
        if len(tied) == 1:
            status = tied[0]
        else:  # no majority: take the middle verdict
            ranks = sorted(_STATUSES.index(s) for s in statuses)
            status = _STATUSES[ranks[(len(ranks) - 1) // 2]]
        if len(counts) > 1:
            split.append(point.id)
        agreeing = [v for v in votes if v is not None and v.status == status]
        # show the verdict whose quote really is in the answer, when there is one
        agreeing.sort(key=lambda v: not (v.evidence and evidence_in_answer(v.evidence, answer)))
        chosen = agreeing[0] if agreeing else PointVerdict(
            point_id=point.id, status=status, marks_awarded=0.0, reason="Markers were split."
        )  # fmt: skip
        out.append(chosen.model_copy(update={"status": status}))
    return apply_mark_rule(Grading(verdicts=out), rubric, partial_weight), split

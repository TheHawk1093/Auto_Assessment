"""Re-price saved verdicts with a different mark rule. No model calls, so it is free and exact.

Used to test how generously verdicts are turned into marks (the partial weight) without
re-running the model. Feedback text is carried over unchanged, so it was written under the
old marks: use rescored runs to compare scores, not to read feedback.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from autograde.pipeline.verify import apply_mark_rule
from autograde.schemas import Result, Rubric


def rescore(
    results: Sequence[Result], rubrics: Mapping[str, Rubric], partial_weight: float
) -> list[Result]:
    """Re-price partial marks on stored results with a new partial-credit weight.

    Args:
        results: Earlier results; baseline ones (no grading) pass through unchanged.
        rubrics: Marking schemes by question key.
        partial_weight: Share of a point's marks given for a partial verdict.

    Returns:
        New results with the changed grading, total and a `rescored` flag.
    """
    out: list[Result] = []
    for r in results:
        if r.grading is None:  # baseline results have no verdicts to re-price
            out.append(r)
            continue
        grading = apply_mark_rule(r.grading, rubrics[r.item.question_key], partial_weight)
        out.append(
            r.model_copy(
                update={
                    "grading": grading,
                    "predicted_mark": grading.total,
                    "flags": [*r.flags, "rescored"],
                }
            )
        )
    return out

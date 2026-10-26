"""Cascade: a cheap model marks every answer, a stronger one re-marks only the unsure ones.

The triggers are read from the cheap model's finished marking, so they cost nothing.
"""

from __future__ import annotations

from collections.abc import Sequence

from autograde.schemas import Grading

TRIGGERS = ("partial", "mid", "unverified", "deduction")
MID_BAND = 0.15  # a total this close to 0 or to full marks is treated as clear-cut


def unsure_because(
    grading: Grading, flags: Sequence[str], max_mark: float, triggers: Sequence[str]
) -> list[str]:
    """Which of the chosen triggers fire for this marking. Empty means the cheap mark stands.

    partial: some point got a partial verdict (the hardest call to make).
    mid: the total is neither near zero nor near full marks.
    unverified: a quoted piece of evidence was not found in the answer.
    deduction: a deduction rule was applied (cheap models apply them too eagerly).
    """
    hit = []
    if "partial" in triggers and any(v.status == "partial" for v in grading.verdicts):
        hit.append("partial")
    if "mid" in triggers and MID_BAND * max_mark < grading.total < (1 - MID_BAND) * max_mark:
        hit.append("mid")
    if "unverified" in triggers and any(f.startswith("unverified_quote") for f in flags):
        hit.append("unverified")
    if "deduction" in triggers and grading.deductions:
        hit.append("deduction")
    return hit

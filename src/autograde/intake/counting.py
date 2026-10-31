"""Which questions count towards a total, when candidates may attempt more than are needed.

A paper that says "answer any three of four" counts each student's best three questions, and a
question the student struck out is not marked at all. A question here is the top-level number
(2a and 2b belong to question 2). This only adds up marks after marking, so it never changes a
marking scheme or a cached result.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from autograde.intake.models import Paper


def group_of(question_id: str) -> str:
    """The top-level question: 2a is part of 2, 3bii of 3. An id with no number is its own group."""
    m = re.match(r"\d+", question_id)
    return m.group(0) if m else question_id


@dataclass
class Counting:
    """Which questions of an exam count towards a student's total (best-of-n rules)."""

    count: int | None = None  # how many questions count; None means all of them
    struck: dict[str, set[str]] = field(default_factory=dict)  # student -> struck-out questions

    def is_struck(self, student: str, question_id: str) -> bool:
        """Say whether this student struck out the question's top-level group."""
        return group_of(question_id) in self.struck.get(student, set())

    @property
    def active(self) -> bool:
        """Say whether any best-of-n rule is in force."""
        return self.count is not None or bool(self.struck)


@dataclass
class Counted:
    """A student's total over the questions that count."""

    total: float
    out_of: float
    groups: list[str]  # the questions that count, in paper order


def counted_total(
    per_question: dict[str, float], paper: Paper, student: str, counting: Counting
) -> Counted:
    """The student's total over the questions that count, and what those questions are worth."""
    worth: dict[str, float] = {}
    got: dict[str, float] = {}
    for q in paper.questions:
        g = group_of(q.id)
        worth[g] = worth.get(g, 0.0) + q.max_mark
        got[g] = got.get(g, 0.0) + per_question.get(q.id, 0.0)
    open_groups = [g for g in worth if g not in counting.struck.get(student, set())]
    n = len(open_groups) if counting.count is None else counting.count
    # best scores first; on a tie the earlier question counts
    best = sorted(open_groups, key=lambda g: (-got[g], open_groups.index(g)))[:n]
    chosen = [g for g in worth if g in best]
    return Counted(
        round(sum(got[g] for g in chosen), 6), round(sum(worth[g] for g in chosen), 6), chosen
    )


def parse_struck(specs: list[str]) -> dict[str, set[str]]:
    """`--struck-out student=3` or `student=1,3` into {student: {"1", "3"}}."""
    out: dict[str, set[str]] = {}
    for spec in specs:
        student, _, qs = spec.partition("=")
        out.setdefault(student.strip(), set()).update(
            group_of(q.strip().lstrip("Qq")) for q in qs.split(",") if q.strip()
        )
    return out

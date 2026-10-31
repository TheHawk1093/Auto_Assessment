"""Code checks for the kind of question, run before marking and applied after it.

Each check gives the marker facts (`evidence`), may add flags for the teacher, and may settle the
points it fully covers (`decide`), so numbers, units and choices are never left to a model.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

from autograde.config import PipelineConfig
from autograde.pipeline.codecheck import code_notes
from autograde.pipeline.figure import Describer, figure_notes
from autograde.pipeline.numeric import decide_numeric, numeric_notes
from autograde.schemas import Grading, Item, Rubric

Decide = Callable[[Grading, Rubric], tuple[Grading, list[str]]]


def _keep(grading: Grading, rubric: Rubric) -> tuple[Grading, list[str]]:
    return grading, []


@dataclass
class Checks:
    """What the code checks found for one answer.

    Attributes:
        evidence: Facts for the marker, as text.
        flags: Flags for the teacher.
        decide: Hook that settles points the code can decide itself.
    """

    evidence: str = ""
    flags: list[str] = field(default_factory=list)
    decide: Decide = _keep


def run_checks(
    item: Item, rubric: Rubric, cfg: PipelineConfig, describe: Describer | None = None
) -> Checks:
    """Run the checks that fit this item (numeric, code, figure) before marking.

    Args:
        item: The answer being marked.
        rubric: Its marking scheme.
        cfg: Pipeline switches (follow-through, code execution, sandbox).
        describe: Vision describer, needed only when the item has figures.

    Returns:
        The evidence text, flags and the hook that decides code-checkable points.
    """
    parts: list[str] = []
    out = Checks()
    follow = bool(item.earlier.strip()) and cfg.teacher.follow_through
    if any(p.numeric for p in rubric.points):
        parts.append(numeric_notes(rubric, item.student_answer, follow))
        out.decide = lambda g, r: _numeric(g, r, item.student_answer, follow)
    if item.kind == "code":
        text, flags = code_notes(item, cfg.code_exec, cfg.code_sandbox)
        parts.append(text)
        out.flags += flags
    if item.figures or item.kind == "diagram":
        text, flags = figure_notes(item, describe)
        parts.append(text)
        out.flags += flags
    out.evidence = "\n\n".join(p for p in parts if p)
    return out


def _numeric(
    grading: Grading, rubric: Rubric, answer: str, follow: bool
) -> tuple[Grading, list[str]]:
    graded, _, flags = decide_numeric(grading, rubric, answer, follow)
    return graded, flags

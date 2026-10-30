"""Stage 3 and 4: mark an answer point by point, then check and if needed redo the marking."""

from __future__ import annotations

import logging

from autograde import prompts
from autograde.llm import LLMClient
from autograde.pipeline.read import reading_block
from autograde.pipeline.verify import (
    apply_mark_rule,
    check_grading,
    finalise_deductions,
    repair,
    unverified_points,
)
from autograde.schemas import Grading, PointVerdict, Question, Reading, Rubric, effective_kind

log = logging.getLogger(__name__)


def build_system(
    has_reading: bool,
    policy: str,
    has_deductions: bool = False,
    has_levels: bool = False,
    granularity: str = "rubric",
    kind: str = "short",
    field: str = "",
    mark_step: float | None = None,
    follow_through: bool = False,
) -> str:
    """The marking instructions: base rules, plus optional reading and essence guidance."""
    parts = [prompts.system("grade")]
    if has_reading:
        parts.append(prompts.system("grade.reading"))
    if policy == "essence":
        parts.append(prompts.system("grade.essence"))
    elif policy == "balanced":
        parts.append(prompts.system("grade.balanced"))
    elif policy == "strict":
        parts.append(prompts.system("grade.strict"))
    if has_deductions:
        parts.append(prompts.system("grade.deductions"))
    if has_levels:
        parts.append(prompts.system("grade.levels"))
    if granularity == "none":
        parts.append(prompts.system("grade.nopartial"))
    elif granularity == "stated":
        parts.append(prompts.system("grade.stated"))
    if mark_step:
        parts.append(prompts.system("grade.step").replace("{step}", f"{mark_step:g}"))
    if follow_through:
        parts.append(prompts.system("grade.followthrough"))
    # prompts per answer type and per subject field: add grade.kind.<kind>.system.md or
    # grade.field.<field>.system.md and they are picked up here
    for name in (f"grade.kind.{kind}", f"grade.field.{field}" if field else ""):
        if name and (text := prompts.optional(name)):
            parts.append(text)
    return "\n\n".join(parts)


def mark_answer(
    question: Question,
    rubric: Rubric,
    answer: str,
    client: LLMClient,
    retries: int = 1,
    reading: Reading | None = None,
    evidence_policy: str = "strict",
    policy: str = "literal",
    partial_weight: float | None = None,
    deductions: bool = False,
    granularity: str = "rubric",
    mark_step: float | None = None,
    notes: str = "",
    evidence: str = "",
    earlier: str = "",
) -> tuple[Grading, list[str]]:
    """Return the checked marking and any flags. Total marks are summed by code, not the model.

    evidence_policy "strict": a quote that cannot be found is a problem; if it survives the
    retry the credit is removed. "flag": only structural problems cause a retry, and credit
    with an unfound quote is kept but flagged, because the reading pass gives an independent
    view of what the student said.

    `notes` are the teacher's instructions for this question, `evidence` is what code checks
    found (numbers, units, syntax, a described drawing) and `earlier` the student's answers to
    earlier parts of a multi-part question. All three are shown to the marker as facts or
    instructions, not as part of the answer.
    """
    if not deductions:
        rubric = rubric.model_copy(update={"deductions": []})
    if not answer.strip():
        return _blank(rubric), ["empty_answer"]

    strict = evidence_policy == "strict"
    has_levels = any(p.levels for p in rubric.points)
    system = build_system(
        reading is not None,
        policy,
        bool(rubric.deductions),
        has_levels,
        granularity,
        effective_kind(question.kind, rubric),
        question.field,
        mark_step,
        bool(earlier.strip()),
    )
    lead = (reading_block(reading) if reading else "") + _context(notes, evidence, earlier)
    retry_note = ""
    grading: Grading | None = None
    for attempt in range(retries + 1):
        user = prompts.render(
            "grade.user",
            question=question.text,
            model_answer=question.model_answer,
            rubric=rubric.render(),
            student_answer=answer,
            extra=lead + retry_note,
        )
        grading = client.ask(system, user, Grading)
        problems = check_grading(grading, rubric, answer, require_evidence=strict)
        if not problems:
            flags = ["retried"] if attempt else []
            return _finish(
                grading, rubric, answer, partial_weight, strict, flags, granularity, mark_step
            )
        log.info("Marking check failed (attempt %d): %s", attempt + 1, problems)
        retry_note = (
            "\nYour previous marking had these problems. Fix them:\n- "
            + "\n- ".join(problems)
            + "\n"
        )
    assert grading is not None
    fixed, flags = repair(grading, rubric, answer, zero_unsupported=strict)
    flags = (["retried"] if retries else []) + flags
    return _finish(fixed, rubric, answer, partial_weight, strict, flags, granularity, mark_step)


def _context(notes: str, evidence: str, earlier: str) -> str:
    """The extra facts for the marker, each under its own heading. Empty when there are none."""
    blocks = [
        ("Teacher's instructions for this question", notes),
        ("Automatic checks (computed by code, treat as facts)", evidence),
        ("The student's answers to earlier parts of this question", earlier),
    ]
    return "".join(f"\n{head}:\n{text.strip()}\n" for head, text in blocks if text.strip())


def _finish(
    grading: Grading,
    rubric: Rubric,
    answer: str,
    partial_weight: float | None,
    strict: bool,
    flags: list[str],
    granularity: str = "rubric",
    mark_step: float | None = None,
) -> tuple[Grading, list[str]]:
    """Check the deductions, price the verdicts, and report unverified quotes."""
    grading, deduction_flags = finalise_deductions(grading, rubric, answer)
    priced = _price(grading, rubric, partial_weight, granularity, mark_step)
    return priced, [*flags, *deduction_flags, *_unverified_flags(priced, answer, strict)]


def _price(
    grading: Grading,
    rubric: Rubric,
    partial_weight: float | None,
    granularity: str = "rubric",
    mark_step: float | None = None,
) -> Grading:
    """Apply the mark rule when one is configured; otherwise keep the model's own marks."""
    if partial_weight is None:
        return grading
    return apply_mark_rule(grading, rubric, partial_weight, granularity, mark_step)


def _unverified_flags(grading: Grading, answer: str, strict: bool) -> list[str]:
    """Credit whose quote was not found. Only reported (not removed) under the flag policy."""
    if strict:
        return []
    return [f"unverified_quote:{pid}" for pid in unverified_points(grading, answer)]


def _blank(rubric: Rubric) -> Grading:
    return Grading(
        verdicts=[
            PointVerdict(
                point_id=p.id, status="not_met", marks_awarded=0, reason="No answer given."
            )
            for p in rubric.points
        ]
    )

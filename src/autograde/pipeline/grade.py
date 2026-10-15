"""Stage 3 and 4: mark an answer point by point, then check and if needed redo the marking."""

from __future__ import annotations

import logging

from autograde import prompts
from autograde.llm import LLMClient
from autograde.pipeline.read import reading_block
from autograde.pipeline.verify import check_grading, repair, unverified_points
from autograde.schemas import Grading, PointVerdict, Question, Reading, Rubric

log = logging.getLogger(__name__)


def build_system(has_reading: bool, policy: str) -> str:
    """The marking instructions: base rules, plus optional reading and essence guidance."""
    parts = [prompts.system("grade")]
    if has_reading:
        parts.append(prompts.system("grade.reading"))
    if policy == "essence":
        parts.append(prompts.system("grade.essence"))
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
) -> tuple[Grading, list[str]]:
    """Return the checked marking and any flags. Total marks are summed by code, not the model.

    evidence_policy "strict": a quote that cannot be found is a problem; if it survives the
    retry the credit is removed. "flag": only structural problems cause a retry, and credit
    with an unfound quote is kept but flagged, because the reading pass gives an independent
    view of what the student said.
    """
    if not answer.strip():
        return _blank(rubric), ["empty_answer"]

    strict = evidence_policy == "strict"
    system = build_system(reading is not None, policy)
    lead = reading_block(reading) if reading else ""
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
            return grading, flags + _unverified_flags(grading, answer, strict)
        log.info("Marking check failed (attempt %d): %s", attempt + 1, problems)
        retry_note = (
            "\nYour previous marking had these problems. Fix them:\n- "
            + "\n- ".join(problems)
            + "\n"
        )
    assert grading is not None
    fixed, flags = repair(grading, rubric, answer, zero_unsupported=strict)
    flags = (["retried"] if retries else []) + flags
    return fixed, flags + _unverified_flags(fixed, answer, strict)


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

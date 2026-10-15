"""Stage 3 and 4: mark an answer point by point, then check and if needed redo the marking."""

from __future__ import annotations

import logging

from autograde import prompts
from autograde.llm import LLMClient
from autograde.pipeline.verify import check_grading, repair
from autograde.schemas import Grading, PointVerdict, Question, Rubric

log = logging.getLogger(__name__)


def mark_answer(
    question: Question, rubric: Rubric, answer: str, client: LLMClient, retries: int = 1
) -> tuple[Grading, list[str]]:
    """Return the checked marking and any flags. Total marks are summed by code, not the model."""
    if not answer.strip():
        return _blank(rubric), ["empty_answer"]

    extra = ""
    grading: Grading | None = None
    problems: list[str] = []
    for attempt in range(retries + 1):
        user = prompts.render(
            "grade.user",
            question=question.text,
            model_answer=question.model_answer,
            rubric=rubric.render(),
            student_answer=answer,
            extra=extra,
        )
        grading = client.ask(prompts.system("grade"), user, Grading)
        problems = check_grading(grading, rubric, answer)
        if not problems:
            return grading, ["retried"] if attempt else []
        log.info("Marking check failed (attempt %d): %s", attempt + 1, problems)
        extra = (
            "\nYour previous marking had these problems. Fix them:\n- "
            + "\n- ".join(problems)
            + "\n"
        )
    assert grading is not None
    fixed, flags = repair(grading, rubric, answer)
    return fixed, ["retried", *flags] if retries else flags


def _blank(rubric: Rubric) -> Grading:
    return Grading(
        verdicts=[
            PointVerdict(
                point_id=p.id, status="not_met", marks_awarded=0, reason="No answer given."
            )
            for p in rubric.points
        ]
    )

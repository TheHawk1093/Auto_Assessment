"""Stage 5: write feedback for the student from the checked marking."""

from __future__ import annotations

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import Feedback, Grading, Item, Rubric


def write_feedback(item: Item, rubric: Rubric, grading: Grading, client: LLMClient) -> Feedback:
    if not item.student_answer.strip():
        return Feedback(
            strengths=[],
            improvements=[],
            summary="No answer was given for this question, so no marks could be awarded.",
        )
    user = prompts.render(
        "feedback.user",
        question=item.question,
        model_answer=item.model_answer,
        student_answer=item.student_answer,
        total=f"{grading.total:g}",
        max_mark=f"{item.max_mark:g}",
        marking=grading.render(rubric),
    )
    return client.ask(prompts.system("feedback"), user, Feedback)

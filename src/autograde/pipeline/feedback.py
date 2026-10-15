"""Stage 5: write feedback for the student from the checked marking."""

from __future__ import annotations

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import Feedback, Grading, Item, Rubric


def write_feedback(
    item: Item,
    rubric: Rubric,
    grading: Grading,
    client: LLMClient,
    variant: str = "standard",
) -> Feedback:
    """standard: say what is missing and the fix | hints: guide the student to the missing idea
    | critique: standard draft, then a second pass that removes vague or generic parts."""
    if not item.student_answer.strip():
        return Feedback(
            strengths=[],
            improvements=[],
            summary="No answer was given for this question, so no marks could be awarded.",
        )
    values = dict(
        question=item.question,
        model_answer=item.model_answer,
        student_answer=item.student_answer,
        total=f"{grading.total:g}",
        max_mark=f"{item.max_mark:g}",
        marking=grading.render(rubric),
    )
    user = prompts.render("feedback.user", **values)
    if variant == "hints":
        return client.ask(prompts.system("feedback.hints"), user, Feedback)
    draft = client.ask(prompts.system("feedback"), user, Feedback)
    if variant == "standard":
        return draft
    critique_user = prompts.render(
        "feedback.critique.user", draft=draft.model_dump_json(indent=2), **values
    )
    return client.ask(prompts.system("feedback.critique"), critique_user, Feedback)

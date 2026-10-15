"""The simplest possible grader: one prompt, one mark. The number every other design must beat."""

from __future__ import annotations

from pydantic import BaseModel

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import Item, Result


class _Mark(BaseModel):
    mark: float


def grade_baseline(item: Item, client: LLMClient) -> Result:
    user = prompts.render(
        "baseline.user",
        question=item.question,
        model_answer=item.model_answer,
        student_answer=item.student_answer,
        max_mark=f"{item.max_mark:g}",
    )
    mark = client.ask(prompts.system("baseline"), user, _Mark).mark
    return Result(item=item, mode="baseline", predicted_mark=min(max(mark, 0.0), item.max_mark))

"""Feedback written without the marking: the writer sees only the question, the model answer and
the student's answer, and finds the gaps itself. Used to test whether the marking adds anything to
the feedback (see `evaluation/feedback_ab.py`)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import Feedback, Improvement, Item


class AloneImprovement(BaseModel):
    kind: Literal["partial", "missed", "incorrect"] = "missed"
    issue: str
    why: str = ""
    fix: str


class AloneFeedback(BaseModel):
    asks: str = ""
    strengths: list[str]
    improvements: list[AloneImprovement]
    summary: str


def write_feedback_alone(item: Item, client: LLMClient) -> Feedback:
    """Feedback from the answers alone. Improvements get ids i1, i2, ... (there are no points)."""
    if not item.student_answer.strip():
        return Feedback(
            strengths=[],
            improvements=[],
            summary="No answer was given for this question, so no marks could be awarded.",
        )
    user = prompts.render(
        "feedback.independent.user",
        question=item.question,
        model_answer=item.model_answer,
        student_answer=item.student_answer,
    )
    raw = client.ask(prompts.system("feedback.independent"), user, AloneFeedback)
    return Feedback(
        asks=raw.asks,
        strengths=raw.strengths,
        improvements=[
            Improvement(point_id=f"i{n}", kind=x.kind, issue=x.issue, why=x.why, fix=x.fix)
            for n, x in enumerate(raw.improvements, 1)
        ],
        summary=raw.summary,
    )

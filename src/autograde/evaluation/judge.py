"""Score the feedback with a second model: a handful of yes/no questions per piece."""

from __future__ import annotations

from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import Result, Rubric

CRITERIA = (
    "anchored",
    "names_missed_point",
    "explains_why",
    "actionable",
    "correct",
    "consistent_with_marks",
)


class Judgement(BaseModel):
    """The feedback judge's verdict on one answer's feedback.

    Each criterion is true, false, or None when it does not apply to the answer. `note` is the
    judge's short comment.
    """

    anchored: bool | None
    names_missed_point: bool | None
    explains_why: bool | None
    actionable: bool | None
    correct: bool | None
    consistent_with_marks: bool | None
    note: str


def judge_one(result: Result, rubric: Rubric, client: LLMClient) -> Judgement:
    """Judge the feedback on one marked answer against its scheme."""
    assert result.grading is not None and result.feedback is not None
    item = result.item
    user = prompts.render(
        "judge.user",
        question=item.question,
        model_answer=item.model_answer,
        student_answer=item.student_answer,
        total=f"{result.grading.total:g}",
        max_mark=f"{item.max_mark:g}",
        marking=result.grading.render(rubric),
        feedback=result.feedback.model_dump_json(indent=2),
    )
    return client.ask(prompts.system("judge"), user, Judgement)


def judge_all(
    results: Sequence[Result], rubrics: dict[str, Rubric], client: LLMClient, workers: int = 4
) -> list[Judgement]:
    """Judge the feedback on every result in parallel, in input order."""
    with ThreadPoolExecutor(workers) as pool:
        return list(pool.map(lambda r: judge_one(r, rubrics[r.item.question_key], client), results))


def pass_rates(judgements: Sequence[Judgement]) -> dict[str, float | None]:
    """Share of 'true' per criterion, ignoring 'not applicable'."""
    rates: dict[str, float | None] = {}
    for c in CRITERIA:
        vals = [v for j in judgements if (v := getattr(j, c)) is not None]
        rates[c] = sum(vals) / len(vals) if vals else None
    return rates

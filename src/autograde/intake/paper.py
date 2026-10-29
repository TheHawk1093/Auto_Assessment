"""Question paper to structured questions with their marks."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field

from autograde import prompts
from autograde.intake.files import read_document
from autograde.intake.models import Paper, QuestionSpec
from autograde.llm import LLMClient

log = logging.getLogger(__name__)


class _Question(QuestionSpec):
    max_mark: float | None = None  # type: ignore[assignment]


class _Draft(BaseModel):
    """What the reader returns; marks may be missing and are then reported, never guessed."""

    title: str = ""
    questions: list[_Question] = Field(default_factory=list)


def load_paper(
    path: Path, client: LLMClient | None = None, single_question_mark: float | None = None
) -> Paper:
    """A structured .json paper is read as it is; any other file is split by the model.

    A file holding one question may leave its marks unprinted; `single_question_mark` then gives
    them. With several questions, missing marks are still refused, never guessed."""
    if path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict) and "questions" in data:
            return Paper.model_validate(data)
    if client is None:
        raise ValueError(f"{path.name} is not a structured paper; a model is needed to read it.")
    draft = client.ask(prompts.system("intake.paper"), read_document(path), _Draft)
    if single_question_mark and len(draft.questions) == 1 and not draft.questions[0].max_mark:
        draft.questions[0].max_mark = single_question_mark
    return _checked(draft)


def _checked(draft: _Draft) -> Paper:
    missing = [q.id for q in draft.questions if not q.max_mark or q.max_mark <= 0]
    if missing:
        raise ValueError(
            f"No marks found for question(s) {missing}. Add the marks to the paper or give "
            "it as JSON."
        )
    return Paper(
        title=draft.title,
        questions=[QuestionSpec.model_validate(q.model_dump()) for q in draft.questions],
    )

"""Reference files (model answers, rubrics, or both in one or two files) matched to questions."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import BaseModel, Field

from autograde import prompts
from autograde.intake.files import read_document
from autograde.intake.models import Paper, Reference
from autograde.llm import LLMClient


class _Entry(BaseModel):
    id: str
    model_answer: str = Field(default="", description="The expected answer, copied word for word.")
    rubric: str = Field(
        default="", description="The marking points and mark split, copied word for word."
    )


class _Draft(BaseModel):
    entries: list[_Entry]


def load_references(
    paths: list[Path], paper: Paper, client: LLMClient | None = None
) -> tuple[dict[str, Reference], list[str]]:
    """Per-question references and a list of warnings (questions without one, unknown ids).

    A .json file keyed by question id is read as it is: {"1a": {"model_answer": "...",
    "rubric": "..."}}. Any other file is matched to the questions by the model, which copies the
    text and does not write or change any of it.
    """
    refs: dict[str, Reference] = {}
    texts = []
    for path in paths:
        direct = _direct(path)
        if direct is not None:
            for qid, ref in direct.items():
                old = refs.get(qid, Reference())
                refs[qid] = Reference(
                    model_answer=ref.model_answer or old.model_answer,
                    rubric=ref.rubric or old.rubric,
                )
        else:
            texts.append(f"=== File: {path.name} ===\n{read_document(path)}")
    if texts:
        if client is None:
            raise ValueError("A model is needed to match the reference files to the questions.")
        listing = "\n".join(
            f"{q.id} ({q.max_mark:g} marks): {q.text[:200]}" for q in paper.questions
        )
        user = f"Questions:\n{listing}\n\n" + "\n\n".join(texts)
        for entry in client.ask(prompts.system("intake.reference"), user, _Draft).entries:
            old = refs.get(entry.id, Reference())
            refs[entry.id] = Reference(
                model_answer=entry.model_answer or old.model_answer,
                rubric=entry.rubric or old.rubric,
            )
    warnings = [
        f"Reference names an unknown question: {qid}" for qid in refs if qid not in paper.ids
    ]
    warnings += [
        f"No reference for question {q.id}: a scheme will be derived from the question alone."
        for q in paper.questions
        if q.id not in refs or not (refs[q.id].model_answer or refs[q.id].rubric)
    ]
    return {k: v for k, v in refs.items() if k in paper.ids}, warnings


def _direct(path: Path) -> dict[str, Reference] | None:
    if path.suffix.lower() != ".json":
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "questions" in data:
        return None
    out = {}
    for qid, value in data.items():
        if isinstance(value, str):
            value = {"model_answer": value}
        if not isinstance(value, dict):
            return None
        rubric = value.get("rubric", "")
        out[str(qid)] = Reference(
            model_answer=str(value.get("model_answer", "")),
            rubric=rubric if isinstance(rubric, str) else json.dumps(rubric),
        )
    return out

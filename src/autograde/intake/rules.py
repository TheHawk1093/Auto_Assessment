"""Exam-wide marking rules read from the paper's instructions and the teacher's rubric."""

from __future__ import annotations

from pathlib import Path

from autograde import prompts
from autograde.config import TeacherInputs
from autograde.intake.files import read_document
from autograde.intake.models import ExamRules
from autograde.llm import LLMClient

_MAX_CHARS = 60_000


def extract_rules(paper_path: Path, reference_paths: list[Path], client: LLMClient) -> ExamRules:
    """The rules the documents state for the whole exam. One model call; nothing is invented."""
    parts = [("Question paper", paper_path), *(("Reference or rubric", p) for p in reference_paths)]
    texts = []
    for label, path in parts:
        if path.suffix.lower() == ".json":
            continue
        texts.append(f"=== {label}: {path.name} ===\n{read_document(path)}")
    if not texts:
        return ExamRules()
    user = "\n\n".join(texts)[:_MAX_CHARS]
    return client.ask(prompts.system("intake.rules"), user, ExamRules)


GRANULARITY = {
    "unstated": "rubric",
    "stated_only": "stated",
    "none": "none",
    "half": "half",
    "quarter": "quarter",
}


def apply_rules(
    rules: ExamRules,
    *,
    granularity: str | None,
    mark_step: float | None,
    strictness: str | None,
    follow_through: bool | None,
    working_required: bool,
    notes: str,
    question_notes: dict[str, str],
) -> TeacherInputs:
    """Teacher inputs where the teacher's own flags win over the rules read from the documents."""
    extra = " ".join(rules.notes)
    return TeacherInputs(
        partial_credit=granularity or GRANULARITY[rules.part_marks],  # type: ignore[arg-type]
        mark_step=mark_step or rules.mark_step,
        strictness=strictness,  # type: ignore[arg-type]
        follow_through=(
            follow_through
            if follow_through is not None
            else True
            if rules.follow_through is None
            else rules.follow_through
        ),
        working_required=working_required or rules.working_required,
        notes=" ".join(t for t in (notes, extra) if t),
        question_notes=question_notes,
    )

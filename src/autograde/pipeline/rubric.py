"""Stage 2: get a marking scheme for each question, write it once, test it, cache it."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

from autograde import prompts
from autograde.config import PipelineConfig, Settings
from autograde.llm import LLMClient, build_client
from autograde.pipeline.grade import mark_answer
from autograde.pipeline.levels import LEVELS, dataset_of, level_prompt
from autograde.schemas import EPS, AtomicFacts, Question, Rubric, RubricDraft, RubricRecord

log = logging.getLogger(__name__)

FULL_CREDIT_SHARE = 0.9  # the model answer must score at least this share of the total
NO_CREDIT_SHARE = 0.1  # a "don't know" answer must score at most this share
NON_ANSWER = "I do not know."


def rubric_prompt(variant: str, dataset: str = "") -> str:
    """Scheme-writing prompt: rubric.system.md by default, rubric.<variant>.system.md otherwise.

    A strictness level (lenient, moderate, harsh) uses the level prompt plus the dataset policy.
    """
    if variant in LEVELS:
        return level_prompt(variant, dataset)
    return prompts.system("rubric" if variant == "generated" else f"rubric.{variant}")


def generate_rubric(
    question: Question, client: LLMClient, note: str = "", variant: str = "generated"
) -> Rubric:
    """Ask for a scheme whose marks add up to the question total, retrying with the error."""
    extra = note
    for _ in range(3):
        user = prompts.render(
            "rubric.user",
            question=question.text,
            model_answer=question.model_answer,
            max_mark=f"{question.max_mark:g}",
            extra=extra,
        )
        system = rubric_prompt(variant, dataset_of(question.key))
        if variant == "atomic":
            rubric = client.ask(system, user, AtomicFacts).to_rubric(question.max_mark)
        else:
            rubric = client.ask(system, user, RubricDraft).to_rubric()
        if abs(rubric.total - question.max_mark) < EPS:
            return rubric.model_copy(update={"level": variant}) if variant in LEVELS else rubric
        extra = (
            f"{note}\nYour previous scheme added up to {rubric.total:g} marks. "
            f"It must add up to exactly {question.max_mark:g}.\n"
        )
    raise ValueError(f"Could not get a scheme totalling {question.max_mark:g} for {question.key}")


def selftest(question: Question, rubric: Rubric, client: LLMClient) -> list[str]:
    """Automatic checks. Returns failure notes, empty if the scheme passes."""
    notes: list[str] = []
    full, _ = mark_answer(question, rubric, question.model_answer, client, retries=0)
    if full.total < FULL_CREDIT_SHARE * question.max_mark:
        notes.append(f"The model answer scored only {full.total:g} of {question.max_mark:g}.")
    blank, _ = mark_answer(question, rubric, NON_ANSWER, client, retries=0)
    if blank.total > NO_CREDIT_SHARE * question.max_mark:
        notes.append(f'A "don\'t know" answer scored {blank.total:g} of {question.max_mark:g}.')
    return notes


def build_record(
    question: Question, client: LLMClient, run_selftest: bool = True, variant: str = "generated"
) -> RubricRecord:
    rubric = generate_rubric(question, client, variant=variant)
    if not run_selftest:
        return RubricRecord(question_key=question.key, rubric=rubric)
    notes = selftest(question, rubric, client)
    if notes:
        log.info("Scheme for %s failed its self-test, rewriting once: %s", question.key, notes)
        hint = "\nA previous scheme failed these tests, so avoid repeating its problems:\n- "
        rubric = generate_rubric(question, client, hint + "\n- ".join(notes) + "\n", variant)
        notes = selftest(question, rubric, client)
    return RubricRecord(
        question_key=question.key, rubric=rubric, selftest_passed=not notes, selftest_notes=notes
    )


class RubricStore:
    """Disk cache of schemes, keyed by model and question, so each is written once."""

    def __init__(
        self,
        rubrics_dir: Path,
        client: LLMClient,
        run_selftest: bool = True,
        variant: str = "generated",
    ) -> None:
        self.rubrics_dir = rubrics_dir
        self.client = client
        self.run_selftest = run_selftest
        self.variant = variant

    def get(self, question: Question) -> RubricRecord:
        path = rubric_path(self.rubrics_dir, self.client.name, question.key, self.variant)
        if path.exists():
            return RubricRecord.model_validate_json(path.read_text(encoding="utf-8"))
        record = build_record(question, self.client, self.run_selftest, self.variant)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(record.model_dump(), indent=2), encoding="utf-8")
        tmp.replace(path)
        return record


def rubric_path(
    rubrics_dir: Path, client_name: str, question_key: str, variant: str = "generated"
) -> Path:
    return rubrics_dir / _slug(client_name) / _slug(variant) / f"{_slug(question_key)}.json"


def cached_record(
    rubrics_dir: Path, client_name: str, question_key: str, variant: str = "generated"
) -> RubricRecord | None:
    """Read a stored scheme without ever calling a model."""
    path = rubric_path(rubrics_dir, client_name, question_key, variant)
    if not path.exists():
        return None
    return RubricRecord.model_validate_json(path.read_text(encoding="utf-8"))


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text)


def store_for(
    settings: Settings, cfg: PipelineConfig | None = None, grader: LLMClient | None = None
):
    """The scheme store a run uses. With `rubric_model`, that model writes the schemes."""
    cfg = cfg or settings.pipeline
    author = grader or build_client(settings.llm)
    if cfg.rubric_model:
        author = build_client(
            settings.llm.model_copy(update={"model": cfg.rubric_model, "effort": None})
        )
    return RubricStore(settings.paths.rubrics_dir, author, cfg.rubric_selftest, cfg.rubric_variant)

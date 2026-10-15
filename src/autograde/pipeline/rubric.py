"""Stage 2: get a marking scheme for each question, write it once, test it, cache it."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path

from autograde import prompts
from autograde.llm import LLMClient
from autograde.pipeline.grade import mark_answer
from autograde.schemas import EPS, Question, Rubric, RubricRecord

log = logging.getLogger(__name__)

FULL_CREDIT_SHARE = 0.9  # the model answer must score at least this share of the total
NO_CREDIT_SHARE = 0.1  # a "don't know" answer must score at most this share
NON_ANSWER = "I do not know."


def generate_rubric(question: Question, client: LLMClient, note: str = "") -> Rubric:
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
        rubric = client.ask(prompts.system("rubric"), user, Rubric)
        if abs(rubric.total - question.max_mark) < EPS:
            return rubric
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


def build_record(question: Question, client: LLMClient, run_selftest: bool = True) -> RubricRecord:
    rubric = generate_rubric(question, client)
    if not run_selftest:
        return RubricRecord(question_key=question.key, rubric=rubric)
    notes = selftest(question, rubric, client)
    if notes:
        log.info("Scheme for %s failed its self-test, rewriting once: %s", question.key, notes)
        hint = "\nA previous scheme failed these tests, so avoid repeating its problems:\n- "
        rubric = generate_rubric(question, client, hint + "\n- ".join(notes) + "\n")
        notes = selftest(question, rubric, client)
    return RubricRecord(
        question_key=question.key, rubric=rubric, selftest_passed=not notes, selftest_notes=notes
    )


class RubricStore:
    """Disk cache of schemes, keyed by model and question, so each is written once."""

    def __init__(self, cache_dir: Path, client: LLMClient, run_selftest: bool = True) -> None:
        self.cache_dir = cache_dir
        self.client = client
        self.run_selftest = run_selftest

    def get(self, question: Question) -> RubricRecord:
        path = rubric_path(self.cache_dir, self.client.name, question.key)
        if path.exists():
            return RubricRecord.model_validate_json(path.read_text(encoding="utf-8"))
        record = build_record(question, self.client, self.run_selftest)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        tmp.write_text(json.dumps(record.model_dump(), indent=2), encoding="utf-8")
        tmp.replace(path)
        return record


def rubric_path(cache_dir: Path, client_name: str, question_key: str) -> Path:
    return cache_dir / "rubrics" / _slug(client_name) / f"{_slug(question_key)}.json"


def cached_record(cache_dir: Path, client_name: str, question_key: str) -> RubricRecord | None:
    """Read a stored scheme without ever calling a model."""
    path = rubric_path(cache_dir, client_name, question_key)
    if not path.exists():
        return None
    return RubricRecord.model_validate_json(path.read_text(encoding="utf-8"))


def _slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", text)

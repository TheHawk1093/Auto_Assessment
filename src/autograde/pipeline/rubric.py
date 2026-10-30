"""Stage 2: get a marking scheme for each question, write it once, test it, cache it."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from pathlib import Path

from autograde import prompts
from autograde.config import PipelineConfig, Settings, TeacherInputs
from autograde.llm import LLMClient, build_client
from autograde.pipeline.grade import mark_answer
from autograde.pipeline.levels import LEVELS, dataset_of, level_prompt
from autograde.pipeline.objective import mcq_record
from autograde.pipeline.verify import GRANULARITY_SHARES
from autograde.schemas import (
    EPS,
    AtomicFacts,
    Question,
    Rubric,
    RubricDraft,
    RubricRecord,
    RubricReview,
    has_reference,
)

log = logging.getLogger(__name__)

FULL_CREDIT_SHARE = 0.9  # the model answer must score at least this share of the total
NO_CREDIT_SHARE = 0.1  # a "don't know" answer must score at most this share
NON_ANSWER = "I do not know."


PART_MARKS = {
    "rubric": "Part marks: use whatever steps suit each point.",
    "stated": (
        "Part marks: only where the rubric names them. Give a point levels only for the part marks "
        "the rubric states; every other point is all or nothing, and do not add levels, leniency "
        "or alternative credit that the rubric does not state."
    ),
    "none": "Part marks: not allowed. Every point is all or nothing, so give no levels.",
    "half": "Part marks: half of a point's marks only. Give at most one level, with share 0.5.",
    "quarter": "Part marks: quarter steps only. Levels may have the shares 0.25, 0.5 and 0.75.",
}
STRICTNESS = {
    "lenient": "Judge generously: credit the central idea in any wording.",
    "moderate": "Judge fairly: the idea must be there and basically right.",
    "strict": "Judge tightly: precise terms, complete statements and correct detail are expected.",
}


def is_solid(variant: str) -> bool:
    """The solid writer, with an optional style: "solid" or "solid.<style>" (rubric.style.*)."""
    return variant == "solid" or variant.startswith("solid.")


def rubric_prompt(variant: str, dataset: str = "", kind: str = "short", field: str = "") -> str:
    """Scheme-writing prompt: rubric.system.md by default, rubric.<variant>.system.md otherwise.

    A strictness level (lenient, moderate, harsh) uses the level prompt plus the dataset policy.
    The "solid" variant uses the general writer plus the part for the answer type.
    """
    if variant in LEVELS:
        return level_prompt(variant, dataset)
    if is_solid(variant):
        style = variant.partition(".")[2]
        names = ["rubric.solid", f"rubric.solid.{kind}"] + (
            [f"rubric.field.{field}"] if field else []
        )
        names += [f"rubric.style.{style}"] if style else []
        return "\n\n".join(t for t in (prompts.optional(n) for n in names) if t)
    return prompts.system("rubric" if variant == "generated" else f"rubric.{variant}")


def teacher_block(teacher: TeacherInputs, key: str) -> str:
    """The teacher's instructions as lines for the scheme writer. Empty when there are none."""
    lines = [PART_MARKS[teacher.partial_credit]] if teacher.partial_credit != "rubric" else []
    if teacher.mark_step:
        lines.append(
            f"Marks are given in steps of {teacher.mark_step:g}: write point marks and part-mark "
            f"levels so that every mark an answer can earn is a multiple of {teacher.mark_step:g}."
        )
    if teacher.strictness:
        lines.append(STRICTNESS[teacher.strictness])
    if note := teacher.for_question(key):
        lines.append(note)
    return "Teacher's instructions:\n- " + "\n- ".join(lines) + "\n" if lines else ""


def variant_dir(variant: str, teacher: TeacherInputs | None = None) -> str:
    """The cache folder of a scheme source. Teacher inputs that change the scheme change it."""
    if not is_solid(variant) or teacher is None or teacher.is_default:
        return variant
    digest = hashlib.sha1(teacher.model_dump_json().encode()).hexdigest()[:8]
    return f"{variant}-{digest}"


def conform(rubric: Rubric, granularity: str) -> Rubric:
    """Make part-mark levels agree with the teacher's granularity, whatever the writer did."""
    if granularity in ("rubric", "stated"):
        return rubric
    allowed = GRANULARITY_SHARES[granularity]
    points = []
    for p in rubric.points:
        levels = {}
        for lv in p.levels if allowed else []:
            share = min(allowed, key=lambda a: abs(a - lv.share))
            levels.setdefault(share, lv.model_copy(update={"share": share}))
        points.append(
            p.model_copy(
                update={
                    "levels": sorted(levels.values(), key=lambda lv: lv.share),
                    "partial_credit": p.partial_credit if allowed else "",
                }
            )
        )
    return rubric.model_copy(update={"points": points})


def structured_rubric(question: Question) -> Rubric | None:
    """The teacher's rubric when it is already points with marks (JSON) that add up to the total."""
    text = question.rubric.strip()
    if not text.startswith("{"):
        return None
    try:
        rubric = Rubric.model_validate_json(text)
    except ValueError:
        return None
    return rubric if abs(rubric.total - question.max_mark) < EPS else None


def generate_rubric(
    question: Question,
    client: LLMClient,
    note: str = "",
    variant: str = "generated",
    teacher: TeacherInputs | None = None,
) -> Rubric:
    """Ask for a scheme whose marks add up to the question total, retrying with the error."""
    teacher = teacher or TeacherInputs()
    given = structured_rubric(question)
    if is_solid(variant) and given is not None:
        return conform(given, teacher.partial_credit)  # the teacher already wrote the points
    extra = (teacher_block(teacher, question.key) if is_solid(variant) else "") + note
    for _ in range(3):
        user = prompts.render(
            "rubric.solid.user" if is_solid(variant) else "rubric.user",
            question=question.text,
            model_answer=question.model_answer,
            rubric=question.rubric.strip() or "Not given.",
            max_mark=f"{question.max_mark:g}",
            extra=extra,
        )
        system = rubric_prompt(variant, dataset_of(question.key), question.kind, question.field)
        if variant == "atomic":
            rubric = client.ask(system, user, AtomicFacts).to_rubric(question.max_mark)
        else:
            rubric = client.ask(system, user, RubricDraft).to_rubric()
        if abs(rubric.total - question.max_mark) < EPS:
            if is_solid(variant):
                rubric = conform(rubric, teacher.partial_credit)
            return rubric.model_copy(update={"level": variant}) if variant in LEVELS else rubric
        extra = (
            f"{note}\nYour previous scheme added up to {rubric.total:g} marks. "
            f"It must add up to exactly {question.max_mark:g}.\n"
        )
    raise ValueError(f"Could not get a scheme totalling {question.max_mark:g} for {question.key}")


def review_rubric(
    question: Question, rubric: Rubric, client: LLMClient, teacher: TeacherInputs
) -> tuple[Rubric, list[str]]:
    """A second look at a draft: returns the scheme to use and the issues that were found."""
    key = f"Answer key the writer worked out:\n{rubric.answer_key}\n" if rubric.answer_key else ""
    user = prompts.render(
        "rubric.review.user",
        question=question.text,
        model_answer=question.model_answer,
        max_mark=f"{question.max_mark:g}",
        extra=teacher_block(teacher, question.key),
        given=question.rubric.strip() or "Not given.",
        rubric=rubric.render(),
        key=key,
    )
    review = client.ask(prompts.system("rubric.review"), user, RubricReview)
    if not review.issues or review.revised is None:
        return rubric, []
    revised = review.revised.to_rubric()
    if abs(revised.total - question.max_mark) > EPS:
        return rubric, [*review.issues, "revision rejected: marks did not add up"]
    if not revised.answer_key:
        revised = revised.model_copy(update={"answer_key": rubric.answer_key})
    return conform(revised, teacher.partial_credit), review.issues


def full_credit_text(question: Question, rubric: Rubric) -> str:
    """An answer that should earn full marks, if one is available: the model answer, or else the
    writer's own answer key. Essay guides describe quality and are not answers."""
    if question.kind == "essay":
        return ""
    if question.kind == "maths" or not has_reference(question.model_answer):
        return rubric.answer_key
    return question.model_answer


def selftest(question: Question, rubric: Rubric, client: LLMClient) -> list[str]:
    """Automatic checks. Returns failure notes, empty if the scheme passes."""
    notes: list[str] = []
    if text := full_credit_text(question, rubric):
        full, _ = mark_answer(question, rubric, text, client, retries=0)
        if full.total < FULL_CREDIT_SHARE * question.max_mark:
            notes.append(f"The model answer scored only {full.total:g} of {question.max_mark:g}.")
    blank, _ = mark_answer(question, rubric, NON_ANSWER, client, retries=0)
    if blank.total > NO_CREDIT_SHARE * question.max_mark:
        notes.append(f'A "don\'t know" answer scored {blank.total:g} of {question.max_mark:g}.')
    return notes


def build_record(
    question: Question,
    client: LLMClient,
    run_selftest: bool = True,
    variant: str = "generated",
    teacher: TeacherInputs | None = None,
    review: str = "off",
) -> RubricRecord:
    rubric = generate_rubric(question, client, variant=variant, teacher=teacher)
    issues: list[str] = []
    unsourced = not question.has_ref
    wanted = review == "always" or (review == "no_reference" and unsourced)
    if is_solid(variant) and wanted:
        rubric, issues = review_rubric(question, rubric, client, teacher or TeacherInputs())
    if not run_selftest:
        return RubricRecord(question_key=question.key, rubric=rubric, review_notes=issues)
    notes = selftest(question, rubric, client)
    if notes:
        log.info("Scheme for %s failed its self-test, rewriting once: %s", question.key, notes)
        hint = "\nA previous scheme failed these tests, so avoid repeating its problems:\n- "
        rubric = generate_rubric(
            question, client, hint + "\n- ".join(notes) + "\n", variant, teacher=teacher
        )
        notes = selftest(question, rubric, client)
    return RubricRecord(
        question_key=question.key,
        rubric=rubric,
        selftest_passed=not notes,
        selftest_notes=notes,
        review_notes=issues,
    )


class RubricStore:
    """Disk cache of schemes, keyed by model and question, so each is written once."""

    def __init__(
        self,
        rubrics_dir: Path,
        client: LLMClient,
        run_selftest: bool = True,
        variant: str = "generated",
        teacher: TeacherInputs | None = None,
        review: str = "off",
    ) -> None:
        self.rubrics_dir = rubrics_dir
        self.client = client
        self.run_selftest = run_selftest
        self.variant = variant
        self.teacher = teacher
        self.review = review

    def get(self, question: Question) -> RubricRecord:
        if question.kind == "mcq":  # a choice is checked by code: nothing to write or cache
            return mcq_record(question, self.client)
        folder = variant_dir(self.variant, self.teacher)
        path = rubric_path(self.rubrics_dir, self.client.name, question.key, folder)
        if path.exists():
            return RubricRecord.model_validate_json(path.read_text(encoding="utf-8"))
        record = build_record(
            question, self.client, self.run_selftest, self.variant, self.teacher, self.review
        )
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


def rubric_client(
    settings: Settings, cfg: PipelineConfig, grader: LLMClient | None = None
) -> LLMClient:
    """The model that writes schemes (and reads the exam's rules): `rubric_model` if set."""
    if not cfg.rubric_model:
        return grader or build_client(settings.llm)
    return build_client(
        settings.llm.model_copy(
            update={
                "model": cfg.rubric_model,
                "effort": None,
                "backend": cfg.strong_backend or settings.llm.backend,
            }
        )
    )


def store_for(
    settings: Settings, cfg: PipelineConfig | None = None, grader: LLMClient | None = None
):
    """The scheme store a run uses. With `rubric_model`, that model writes the schemes."""
    cfg = cfg or settings.pipeline
    author = rubric_client(settings, cfg, grader)
    return RubricStore(
        settings.paths.rubrics_dir,
        author,
        cfg.rubric_selftest,
        cfg.rubric_variant,
        cfg.teacher,
        cfg.rubric_review,
    )

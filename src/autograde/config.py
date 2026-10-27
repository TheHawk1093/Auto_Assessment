"""Settings loaded from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

DEFAULT_CONFIG = Path("configs/default.yaml")
FEEDBACK_STYLES = ("standard", "hints", "critique", "formal", "brief", "detailed", "coach")


class LLMConfig(BaseModel):
    backend: Literal["claude_cli", "anthropic", "openrouter", "goedel"] = "claude_cli"
    model: str = "sonnet"
    effort: str | None = None  # claude_cli only: low | medium | high | xhigh | max
    timeout_s: int = 240
    retries: int = 2


class ReaderConfig(BaseModel):
    """One model that reads photographed answer sheets (it must accept images)."""

    provider: Literal["gemini", "openrouter", "claude_cli"] = "gemini"
    model: str = "gemini-3.5-flash-lite"  # gemini and openrouter models must be free ones
    plain: bool = False  # page text only, no question split; for slow reasoning models


class ReaderRoute(BaseModel):
    """Re-read pages whose text is of one kind with a reader chosen for that kind."""

    when: Literal["german", "math"]
    reader: ReaderConfig


class OcrConfig(BaseModel):
    """The reading step: the first reader is tried on each page, then the fallbacks in order.

    With routes, the page text from that read is classified (German prose, formulas and matrices)
    and a matching route re-reads the page with its own reader. If that reader fails, the first
    read is kept.
    """

    reader: ReaderConfig = ReaderConfig()
    fallbacks: list[ReaderConfig] = []
    routes: list[ReaderRoute] = []


class TeacherInputs(BaseModel):
    """What a teacher can say about how this exam is marked. Everything has a sensible default.

    These are the only human inputs at run time; nothing here is tuned to a dataset.
    """

    partial_credit: Literal["rubric", "none", "half", "quarter"] = "rubric"
    # rubric: the rubric's own levels. none: all or nothing. half: 0.5. quarter: 0.25, 0.5, 0.75.
    strictness: Literal["lenient", "moderate", "strict"] | None = None  # how tightly to judge
    notes: str = ""  # free text for every question, e.g. "units are required"
    question_notes: dict[str, str] = {}  # the same, for one question key

    def for_question(self, key: str) -> str:
        return " ".join(t for t in (self.notes, self.question_notes.get(key, "")) if t).strip()

    @property
    def is_default(self) -> bool:
        return self == TeacherInputs()


class PipelineConfig(BaseModel):
    rubric_selftest: bool = True
    read_first: bool = True  # a first pass reads the answer before marking
    evidence_policy: Literal["strict", "flag"] = "flag"  # strict: drop credit with unfound quotes
    policy: Literal["literal", "essence"] = "essence"  # how generously to judge a point
    mark_rule: Literal["status", "model"] = "status"  # status: code turns verdicts into marks
    partial_weight: float = 0.5  # share of a point's marks given for a partial verdict
    rubric_variant: str = "generated"  # lets a different scheme source live beside the default
    rubric_review: Literal["off", "no_reference", "always"] = "no_reference"  # solid variant only
    teacher: TeacherInputs = TeacherInputs()
    feedback_variant: Literal[*FEEDBACK_STYLES] = "formal"
    votes: int = 1  # mark each answer this many times; the majority verdict per point wins
    second_model: str | None = None  # a cheaper model also marks; a big gap flags the answer
    disagree_gap: float = 0.15  # share of the total marks that counts as a big gap
    escalate_model: str | None = None  # a stronger model re-marks the answers the cheap one doubts
    escalate_when: list[str] = ["partial", "mid", "deduction"]  # see pipeline/cascade
    with_feedback: bool = True  # False: mark only (cheaper while tuning the grader)
    feedback_n: int = 1  # write this many feedback drafts and keep the best
    deductions: bool = False  # apply the rubric's deductions (needs a strong marker; see DESIGN)
    strong_backend: Literal["claude_cli", "anthropic", "openrouter", "goedel"] | None = (
        None  # backend of rubric_model and escalate_model; default: the grader's
    )
    rubric_model: str | None = None  # a stronger model writes the schemes once per question
    ocr: Literal["light", "medium", "heavy"] | None = None  # answers are OCR text of this noise
    grade_retries: int = 1
    max_workers: int = 4


class PathsConfig(BaseModel):
    data_dir: Path = Path("data/raw")
    rubrics_dir: Path = Path("rubrics")
    runs_dir: Path = Path("runs")


class Settings(BaseModel):
    llm: LLMConfig = LLMConfig()
    judge: LLMConfig = LLMConfig(model="haiku")
    student: LLMConfig = LLMConfig(model="haiku")  # plays the student in the revision test
    pipeline: PipelineConfig = PipelineConfig()
    ocr: OcrConfig = OcrConfig()
    paths: PathsConfig = PathsConfig()


def load_settings(path: Path | None = None) -> Settings:
    """Load settings from `path`, or the default file if it exists, else built-in defaults."""
    if path is not None and not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")  # never fall back silently
    path = path or DEFAULT_CONFIG
    if not path.exists():
        return Settings()
    return Settings.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})

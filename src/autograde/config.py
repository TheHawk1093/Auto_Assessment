"""Settings loaded from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

DEFAULT_CONFIG = Path("configs/default.yaml")
FEEDBACK_STYLES = ("standard", "hints", "critique", "formal", "brief", "detailed", "coach")


class LLMConfig(BaseModel):
    backend: Literal["claude_cli", "anthropic"] = "claude_cli"
    model: str = "sonnet"
    effort: str | None = None  # claude_cli only: low | medium | high | xhigh | max
    timeout_s: int = 240
    retries: int = 2


class PipelineConfig(BaseModel):
    rubric_selftest: bool = True
    read_first: bool = True  # a first pass reads the answer before marking
    evidence_policy: Literal["strict", "flag"] = "flag"  # strict: drop credit with unfound quotes
    policy: Literal["literal", "essence"] = "essence"  # how generously to judge a point
    mark_rule: Literal["status", "model"] = "status"  # status: code turns verdicts into marks
    partial_weight: float = 0.9  # share of a point's marks given for a partial verdict
    rubric_variant: str = "generated"  # lets a different scheme source live beside the default
    feedback_variant: Literal[*FEEDBACK_STYLES] = "formal"
    votes: int = 1  # mark each answer this many times; the majority verdict per point wins
    second_model: str | None = None  # a cheaper model also marks; a big gap flags the answer
    disagree_gap: float = 0.15  # share of the total marks that counts as a big gap
    with_feedback: bool = True  # False: mark only (cheaper while tuning the grader)
    feedback_n: int = 1  # write this many feedback drafts and keep the best
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
    paths: PathsConfig = PathsConfig()


def load_settings(path: Path | None = None) -> Settings:
    """Load settings from `path`, or the default file if it exists, else built-in defaults."""
    path = path or DEFAULT_CONFIG
    if not path.exists():
        return Settings()
    return Settings.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})

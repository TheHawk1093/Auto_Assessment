"""Settings loaded from YAML."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

DEFAULT_CONFIG = Path("configs/default.yaml")


class LLMConfig(BaseModel):
    backend: Literal["claude_cli", "anthropic"] = "claude_cli"
    model: str = "sonnet"
    timeout_s: int = 240
    retries: int = 2


class PipelineConfig(BaseModel):
    rubric_selftest: bool = True
    read_first: bool = True  # a first pass reads the answer before marking
    evidence_policy: Literal["strict", "flag"] = "flag"  # strict: drop credit with unfound quotes
    rubric_variant: str = "generated"  # lets a different scheme source live beside the default
    grade_retries: int = 1
    max_workers: int = 4


class PathsConfig(BaseModel):
    data_dir: Path = Path("data/raw")
    cache_dir: Path = Path("data/cache")
    runs_dir: Path = Path("runs")


class Settings(BaseModel):
    llm: LLMConfig = LLMConfig()
    judge: LLMConfig = LLMConfig(model="haiku")
    pipeline: PipelineConfig = PipelineConfig()
    paths: PathsConfig = PathsConfig()


def load_settings(path: Path | None = None) -> Settings:
    """Load settings from `path`, or the default file if it exists, else built-in defaults."""
    path = path or DEFAULT_CONFIG
    if not path.exists():
        return Settings()
    return Settings.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")) or {})

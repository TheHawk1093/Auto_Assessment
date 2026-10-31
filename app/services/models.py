"""Which AI models a teacher may choose for marking, and the config that makes a run use one.

The command line already takes backend, model and effort from a YAML config, so the app does not
re-implement any of that: it writes a per-exam config (the base `configs/exam.yaml` with the
model fields replaced) and passes it with `--config`. The administrator decides which options
are available; OpenRouter options are listed but locked until the admin enables them.

To add a model: add one `ModelOption` to CATALOGUE.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from dataclasses import dataclass, replace
from pathlib import Path

import yaml

from app import config
from app.services import db

PATH = config.APP_DATA / "models.json"  # the admin's choices; module-level for tests
DEFAULT = "deepseek-flash"

COST = {
    "free": "Free",
    "plan": "Uses your Claude plan",
    "paid": "Paid per use (OpenRouter)",
}
TIER = {"fast": "Fast", "balanced": "Balanced", "best": "Most careful"}


@dataclass(frozen=True)
class ModelOption:
    """One choice in the model menu: which backend and model, and what it needs to run."""

    id: str
    label: str
    blurb: str
    backend: str  # claude_cli | goedel | openrouter | anthropic | gemini
    model: str
    tier: str  # fast | balanced | best
    cost: str  # free | plan | paid
    effort: str | None = None  # claude_cli only
    rubric_model: str | None = None  # a different model writes the marking schemes
    rubric_backend: str | None = None
    needs: str = ""  # what must be present: claude | goedel | openrouter

    @property
    def key_var(self) -> str:
        """Name of the environment variable holding the API key, or empty if none."""
        return {"goedel": "GOEDEL_API_KEY", "openrouter": "OPENROUTER_API_KEY"}.get(self.needs, "")


CATALOGUE: list[ModelOption] = [
    ModelOption(
        "deepseek-flash", "DeepSeek V4.1 Flash",
        "The default. Quick and free; a good first choice for most exams.",
        "goedel", "deepseek/deepseek-v4.1-flash", "fast", "free", needs="goedel",
    ),
    ModelOption(
        "claude-haiku", "Claude Haiku",
        "Quick and inexpensive; careful enough for short answers.",
        "claude_cli", "haiku", "fast", "plan", effort="low", needs="claude",
    ),
    ModelOption(
        "claude-sonnet", "Claude Sonnet",
        "A balanced choice for most subjects, including working and maths.",
        "claude_cli", "sonnet", "balanced", "plan", effort="low", needs="claude",
    ),
    ModelOption(
        "claude-sonnet-careful", "Claude Sonnet, high effort",
        "Thinks longer before marking. Slower; use for hard questions.",
        "claude_cli", "sonnet", "best", "plan", effort="high", needs="claude",
    ),
    ModelOption(
        "claude-opus", "Claude Opus",
        "The most careful option. Slowest; use for high-stakes marking.",
        "claude_cli", "opus", "best", "plan", effort="medium", needs="claude",
    ),
    ModelOption(
        "deepseek-sonnet-schemes", "DeepSeek marks, Claude Sonnet writes the schemes",
        "Marks cheaply, but the marking scheme for each question is written by a stronger model.",
        "goedel", "deepseek/deepseek-v4.1-flash", "balanced", "plan",
        rubric_model="sonnet", rubric_backend="claude_cli", needs="goedel",
    ),
    ModelOption(
        "or-claude-sonnet", "Claude Sonnet via OpenRouter",
        "Locked until the administrator enables OpenRouter.",
        "openrouter", "anthropic/claude-sonnet-4.5", "balanced", "paid", needs="openrouter",
    ),
    ModelOption(
        "or-deepseek", "DeepSeek via OpenRouter",
        "Locked until the administrator enables OpenRouter.",
        "openrouter", "deepseek/deepseek-chat", "fast", "paid", needs="openrouter",
    ),
]  # fmt: skip


@dataclass(frozen=True)
class ReaderOption:
    """A model that reads handwritten or scanned sheets (it must accept images)."""

    id: str
    label: str
    blurb: str
    provider: str  # gemini | claude_cli
    model: str
    cost: str  # free | plan
    needs: str  # gemini | claude


READERS: list[ReaderOption] = [
    ReaderOption(
        "gemini-lite", "Gemini 3.5 Flash-Lite",
        "Free and quick. Good on neat handwriting; the free tier may keep the images.",
        "gemini", "gemini-3.5-flash-lite", "free", "gemini",
    ),
    ReaderOption(
        "gemini-flash", "Gemini 2.5 Flash",
        "Free. A little slower, often better on untidy handwriting and Indic scripts.",
        "gemini", "gemini-2.5-flash", "free", "gemini",
    ),
    ReaderOption(
        "claude-haiku-read", "Claude Haiku",
        "Uses your Claude plan. Images stay with Anthropic.",
        "claude_cli", "haiku", "plan", "claude",
    ),
    ReaderOption(
        "claude-sonnet-read", "Claude Sonnet",
        "Uses your Claude plan. The most accurate on difficult handwriting.",
        "claude_cli", "sonnet", "plan", "claude",
    ),
]  # fmt: skip
DEFAULT_READER = "gemini-lite"


# ---------- the admin's choices ----------


def _load() -> dict:
    try:
        return json.loads(PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _save(data: dict) -> None:
    PATH.parent.mkdir(parents=True, exist_ok=True)
    PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")


def catalogue() -> list[ModelOption]:
    """Return the options, with any model id the admin has edited."""
    ids = _load().get("model_ids", {})
    return [replace(o, model=ids[o.id]) if ids.get(o.id) else o for o in CATALOGUE]


def get(option_id: str) -> ModelOption:
    """Return the option with this id, or the default if it is unknown."""
    for o in catalogue():
        if o.id == option_id:
            return o
    return get(DEFAULT)


def is_enabled(option: ModelOption) -> bool:
    """On unless the admin turned it off; OpenRouter options are off until turned on."""
    default = option.needs != "openrouter"
    return bool(_load().get("enabled", {}).get(option.id, default))


def set_enabled(option_id: str, enabled: bool, by: str) -> None:
    """Turn an option on or off for teachers (admin choice, audited)."""
    data = _load()
    data.setdefault("enabled", {})[option_id] = enabled
    _save(data)
    db.audit(by, "model_enabled" if enabled else "model_disabled", option_id)


def set_model_id(option_id: str, model: str, by: str) -> None:
    """Replace the model id an option sends to its backend (admin choice, audited)."""
    data = _load()
    data.setdefault("model_ids", {})[option_id] = model.strip()
    _save(data)
    db.audit(by, "model_id", f"{option_id} -> {model.strip()}")


# ---------- can it run here? ----------


def _has_key(var: str) -> bool:
    """Say whether the key is set, in the environment or in .env.

    Only the name is looked for; the value is never read into the app or shown.
    """
    if os.environ.get(var):
        return True
    env = config.ROOT / ".env"
    if not env.exists():
        return False
    pattern = re.compile(rf"^\s*(?:export\s+)?{re.escape(var)}\s*=\s*\S")
    return any(pattern.match(line) for line in env.read_text(encoding="utf-8").splitlines())


def availability(option: ModelOption) -> tuple[bool, str]:
    """(usable now, why not). Checks the admin's switch, then what the machine has."""
    if not is_enabled(option):
        if option.needs == "openrouter":
            return False, "OpenRouter is switched off by the administrator."
        return False, "Switched off by the administrator."
    if option.needs == "claude" and not shutil.which("claude"):
        return False, "The Claude CLI is not installed on this machine."
    if option.key_var and not _has_key(option.key_var):
        return False, f"{option.key_var} is not set (environment or .env)."
    return True, ""


def get_reader(option_id: str) -> ReaderOption:
    """Return the reader with this id, or the default if it is unknown."""
    return next((r for r in READERS if r.id == option_id), READERS[0])


def reader_availability(option: ReaderOption) -> tuple[bool, str]:
    """(usable now, why not) for a reader: the admin's switch, then the key or the CLI."""
    if not bool(_load().get("enabled", {}).get(option.id, True)):
        return False, "Switched off by the administrator."
    if option.needs == "claude" and not shutil.which("claude"):
        return False, "The Claude CLI is not installed on this machine."
    if option.needs == "gemini" and not _has_key("GEMINI_API_KEY"):
        return False, "GEMINI_API_KEY is not set (environment or .env)."
    return True, ""


def usable_readers() -> list[ReaderOption]:
    """Return the readers that can be used now."""
    return [r for r in READERS if reader_availability(r)[0]]


def usable() -> list[ModelOption]:
    """Return the options that can be used now."""
    return [o for o in catalogue() if availability(o)[0]]


# ---------- the per-exam config ----------


def exam_config(option: ModelOption) -> dict:
    """configs/exam.yaml with the model fields of `option`. Everything else is as the CLI has it."""
    cfg = yaml.safe_load((config.ROOT / config.AUTOGRADE_CONFIG).read_text(encoding="utf-8"))
    llm = {**cfg["llm"], "backend": option.backend, "model": option.model}
    llm.pop("effort", None)
    if option.effort:
        llm["effort"] = option.effort
    cfg["llm"] = llm
    cfg["pipeline"] = {
        **cfg["pipeline"],
        "rubric_model": option.rubric_model or option.model,
        "strong_backend": option.rubric_backend or option.backend,
    }
    return cfg


def write_config(option: ModelOption, path: Path) -> Path:
    """Write the per-exam config for `option` to `path` and return the path."""
    path.write_text(yaml.safe_dump(exam_config(option), sort_keys=False), encoding="utf-8")
    return path

"""Which AI models a teacher may choose for marking, and the config that makes a run use one.

The command line already takes backend, model and effort from a YAML config, so the app does not
re-implement any of that: it writes a per-exam config (the base `configs/exam.yaml` with the
model fields replaced) and passes it with `--config`. The administrator decides which options
teachers see. Teachers see only a name, what it suits and what it costs, never how it is wired.

To add a model: add one `ModelOption` to CATALOGUE.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, replace
from pathlib import Path

import yaml

from app import config
from app.services import db

PATH = config.APP_DATA / "models.json"  # the admin's choices; module-level for tests
DEFAULT = "deepseek-flash"
DEFAULT_READER = "gemini-lite"


@dataclass(frozen=True)
class ModelOption:
    """One choice in the model menu: what it suits, what it costs, and the model id."""

    id: str
    label: str
    use: str  # what it suits, in a sentence
    price: str  # cost as listed on OpenRouter
    model: str  # the OpenRouter model id
    rubric_model: str | None = None  # a different model writes the marking schemes

    @property
    def blurb(self) -> str:
        """Suits and cost, as one short text for teachers."""
        return f"{self.use} {self.price}"


CATALOGUE: list[ModelOption] = [
    ModelOption(
        "deepseek-flash", "DeepSeek V4.1 Flash",
        "Suits most exams: short answers, definitions, routine working.",
        "Cost: $0.045 in / $0.50 out per 1M tokens (about 2 cents for 40 answers).",
        "deepseek/deepseek-v4.1-flash",
    ),
    ModelOption(
        "claude-haiku", "Claude Haiku",
        "Suits maths, long working and answers where partial credit needs judgement.",
        "Cost: $1 in / $5 out per 1M tokens.",
        "anthropic/claude-haiku-4.5",
    ),
    ModelOption(
        "deepseek-haiku-schemes", "DeepSeek, with Claude Haiku marking schemes",
        "Suits open-ended answers where the marking scheme matters most.",
        "Cost: DeepSeek rates above, plus Haiku ($1 in / $5 out) once per question.",
        "deepseek/deepseek-v4.1-flash", rubric_model="anthropic/claude-haiku-4.5",
    ),
    ModelOption(
        "claude-sonnet", "Claude Sonnet",
        "Suits the hardest maths and long answers where every mark must be argued.",
        "Cost: $3 in / $15 out per 1M tokens (about $1 for 40 answers).",
        "anthropic/claude-sonnet-4.5",
    ),
    ModelOption(
        "gpt-mini", "GPT-5.4 mini",
        "Suits short answers and routine working when you prefer an OpenAI model.",
        "Cost: $0.75 in / $4.50 out per 1M tokens.",
        "openai/gpt-5.4-mini",
    ),
]  # fmt: skip
DEFAULT = "deepseek-flash"


@dataclass(frozen=True)
class ReaderOption:
    """A model that reads handwritten or scanned sheets (it must accept images)."""

    id: str
    label: str
    use: str
    price: str
    provider: str  # openrouter | bodhan
    model: str

    @property
    def blurb(self) -> str:
        """Suits and cost, as one short text for teachers."""
        return f"{self.use} {self.price}"


READERS: list[ReaderOption] = [
    ReaderOption(
        "gemini-lite", "Gemini 3.5 Flash-Lite",
        "Suits neat handwriting in English. Quick.",
        "Cost: $0.30 in / $2.50 out per 1M tokens.",
        "openrouter", "google/gemini-3.5-flash-lite",
    ),
    ReaderOption(
        "gemini-flash", "Gemini 3.6 Flash",
        "Suits untidy handwriting, or when the quick reader is unsure of many words.",
        "Cost: $0.75 in / $3.75 out per 1M tokens.",
        "openrouter", "google/gemini-3.6-flash",
    ),
    ReaderOption(
        "bodhan", "Bodhan IndicOCR",
        "Suits Hindi, Marathi and other Indian-language handwriting.",
        "Cost: about Rs 0.20 per page.",
        "bodhan", "indic-ocr",
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
    """On unless the admin turned it off."""
    return bool(_load().get("enabled", {}).get(option.id, True))


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
    """(usable now, why not). Checks the admin's switch, then the OpenRouter key."""
    if not is_enabled(option):
        return False, "Switched off by the administrator."
    if not _has_key("OPENROUTER_API_KEY"):
        return False, "OPENROUTER_API_KEY is not set (environment or .env)."
    return True, ""


def get_reader(option_id: str) -> ReaderOption:
    """Return the reader with this id, or the default if it is unknown."""
    return next((r for r in READERS if r.id == option_id), READERS[0])


def reader_availability(option: ReaderOption) -> tuple[bool, str]:
    """(usable now, why not) for a reader: the admin's switch, then its API key."""
    if not bool(_load().get("enabled", {}).get(option.id, True)):
        return False, "Switched off by the administrator."
    var = "INDIC_OCR_API_KEY" if option.provider == "bodhan" else "OPENROUTER_API_KEY"
    if not _has_key(var):
        return False, f"{var} is not set (environment or .env)."
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
    cfg["llm"] = {**cfg["llm"], "backend": "openrouter", "model": option.model}
    cfg["pipeline"] = {
        **cfg["pipeline"],
        "rubric_model": option.rubric_model or option.model,
        "strong_backend": "openrouter",
    }
    return cfg


def write_config(option: ModelOption, path: Path) -> Path:
    """Write the per-exam config for `option` to `path` and return the path."""
    path.write_text(yaml.safe_dump(exam_config(option), sort_keys=False), encoding="utf-8")
    return path

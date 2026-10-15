"""Model-agnostic client. Every stage talks to the model only through `LLMClient.ask`."""

from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from typing import TypeVar

from pydantic import BaseModel, ValidationError

log = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """The model call failed or returned something unusable."""


@dataclass
class Usage:
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    def add(self, other: Usage) -> None:
        self.calls += other.calls
        self.input_tokens += other.input_tokens
        self.output_tokens += other.output_tokens
        self.cost_usd += other.cost_usd

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


class LLMClient(ABC):
    """Ask a model for JSON that matches a pydantic class. Thread-safe usage accounting."""

    def __init__(self, retries: int = 2) -> None:
        self.retries = retries
        self.usage = Usage()
        self._lock = threading.Lock()

    @property
    @abstractmethod
    def name(self) -> str:
        """Short label used in cache paths, e.g. 'claude_cli-sonnet'."""

    @abstractmethod
    def _complete(self, system: str, user: str, schema: dict) -> tuple[dict, Usage]:
        """Return the parsed JSON object and the usage for this one call."""

    def ask(self, system: str, user: str, model: type[T]) -> T:
        schema = model.model_json_schema()
        last: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                data, usage = self._complete(system, user, schema)
            except LLMError as exc:
                last = exc
                log.warning("LLM call failed (attempt %d): %s", attempt + 1, exc)
                continue
            with self._lock:
                self.usage.add(usage)
            try:
                return model.model_validate(data)
            except ValidationError as exc:
                last = exc
                log.warning("Schema mismatch (attempt %d): %s", attempt + 1, exc.errors()[:2])
        raise LLMError(f"Giving up after {self.retries + 1} attempts: {last}")

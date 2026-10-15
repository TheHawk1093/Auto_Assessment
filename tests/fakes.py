"""A scripted model for tests: no network, no CLI."""

from __future__ import annotations

from collections.abc import Callable

from pydantic import BaseModel

from autograde.llm.base import LLMClient, Usage


class FakeClient(LLMClient):
    """Answers each requested schema with a handler. Records every call."""

    def __init__(self, handlers: dict[type[BaseModel], Callable[[str], dict]]) -> None:
        super().__init__(retries=0)
        self.handlers = handlers
        self.calls: list[tuple[type[BaseModel], str]] = []

    @property
    def name(self) -> str:
        return "fake"

    def _complete(self, system: str, user: str, schema: dict) -> tuple[dict, Usage]:
        raise NotImplementedError

    def ask(self, system: str, user: str, model):  # type: ignore[override]
        self.calls.append((model, user))
        self.usage.add(Usage(calls=1))
        return model.model_validate(self.handlers[model](user))

    def count(self, model: type[BaseModel]) -> int:
        return sum(m is model for m, _ in self.calls)

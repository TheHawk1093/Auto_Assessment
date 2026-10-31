"""LLM clients."""

from __future__ import annotations

from autograde.config import LLMConfig
from autograde.llm.base import LLMClient, LLMError, Usage

__all__ = ["LLMClient", "LLMError", "Usage", "build_client", "client_name"]


def build_client(cfg: LLMConfig) -> LLMClient:
    """Create the client named in the config. Imports are lazy so optional extras stay optional."""
    if cfg.backend == "mock":
        from autograde.llm.mock import MockClient

        return MockClient(cfg.model)
    from autograde.llm.openrouter import OpenRouterClient

    return OpenRouterClient(cfg.model, cfg.timeout_s, cfg.retries)


def client_name(cfg: LLMConfig) -> str:
    """The name a client built from `cfg` reports; it keys the stored marking schemes."""
    return f"{cfg.backend}-{cfg.model}"

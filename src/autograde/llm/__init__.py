"""LLM clients."""

from __future__ import annotations

from autograde.config import LLMConfig
from autograde.llm.base import LLMClient, LLMError, Usage

__all__ = ["LLMClient", "LLMError", "Usage", "build_client", "client_name"]


def build_client(cfg: LLMConfig) -> LLMClient:
    """Create the client named in the config. Imports are lazy so optional extras stay optional."""
    if cfg.backend == "claude_cli":
        from autograde.llm.claude_cli import ClaudeCLIClient

        return ClaudeCLIClient(cfg.model, cfg.timeout_s, cfg.retries, cfg.effort)
    from autograde.llm.anthropic_api import AnthropicClient

    return AnthropicClient(cfg.model, cfg.timeout_s, cfg.retries)


def client_name(cfg: LLMConfig) -> str:
    """The name a client built from `cfg` reports; it keys the stored marking schemes."""
    return f"{cfg.backend}-{cfg.model}" + (f"-{cfg.effort}" if cfg.effort else "")

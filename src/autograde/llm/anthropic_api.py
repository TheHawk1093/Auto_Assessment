"""Backend for the Anthropic API (install with `pip install -e .[anthropic]`).

Structured output is obtained by forcing a single tool call whose input schema is the
requested JSON schema. Cost is not computed here; token counts are recorded.
"""

from __future__ import annotations

from autograde.llm.base import LLMClient, LLMError, Usage


class AnthropicClient(LLMClient):
    def __init__(
        self, model: str, timeout_s: int = 240, retries: int = 2, max_tokens: int = 4096
    ) -> None:
        super().__init__(retries)
        try:
            import anthropic
        except ImportError as exc:
            raise LLMError("Install the extra: pip install -e .[anthropic]") from exc
        self._anthropic = anthropic
        self._client = anthropic.Anthropic(timeout=timeout_s)  # reads ANTHROPIC_API_KEY
        self.model = model
        self.max_tokens = max_tokens

    @property
    def name(self) -> str:
        return f"anthropic-{self.model}"

    def _complete(self, system: str, user: str, schema: dict) -> tuple[dict, Usage]:
        try:
            resp = self._client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
                tools=[{"name": "respond", "description": "Return the result.",
                        "input_schema": schema}],
                tool_choice={"type": "tool", "name": "respond"},
            )  # fmt: skip
        except self._anthropic.APIError as exc:
            raise LLMError(f"Anthropic API error: {exc}") from exc
        block = next((b for b in resp.content if b.type == "tool_use"), None)
        if block is None:
            raise LLMError("No tool_use block in the response")
        usage = Usage(
            calls=1, input_tokens=resp.usage.input_tokens, output_tokens=resp.usage.output_tokens
        )
        return dict(block.input), usage

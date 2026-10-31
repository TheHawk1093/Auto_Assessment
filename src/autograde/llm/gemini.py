"""Backend for Google Gemini through the Gemini API, for marking and feedback (text only).

Only the models on the free-tier allow-list are accepted, the same list the OCR readers use, so a
mistake in a config cannot start spending money. The key is GEMINI_API_KEY (environment or the
git-ignored .env). The JSON schema is given in the prompt and the reply is parsed from the first
JSON object, as in the other hosted backends.
"""

from __future__ import annotations

import json

from autograde.llm.base import LLMClient, LLMError, Usage
from autograde.llm.openrouter import first_json_object
from autograde.ocr.hosted import GEMINI_FREE, GEMINI_URL, _call, _key


class GeminiClient(LLMClient):
    """Text client for free-tier Gemini models."""

    prefix = "gemini"

    def __init__(self, model: str, timeout_s: int = 240, retries: int = 2) -> None:
        """Check the model is on the free-tier allow-list."""
        super().__init__(retries)
        if model not in GEMINI_FREE:
            raise LLMError(f"{model!r} is not on the free-tier allow-list: {sorted(GEMINI_FREE)}")
        self.model = model
        self.timeout_s = timeout_s

    @property
    def name(self) -> str:
        """Cache label, e.g. 'gemini-<model>'."""
        return f"{self.prefix}-{self.model}"

    def _complete(self, system: str, user: str, schema: dict) -> tuple[dict, Usage]:
        fmt = (
            "Reply with one JSON object only, no other text, matching this JSON schema:\n"
            + json.dumps(schema)
        )
        body = {
            "system_instruction": {"parts": [{"text": f"{system}\n\n{fmt}"}]},
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {
                "temperature": 0,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json",
            },
        }
        out = _call(
            GEMINI_URL.format(model=self.model), {"x-goog-api-key": _key("GEMINI_API_KEY")}, body
        )
        candidates = out.get("candidates") or []
        if not candidates:
            raise LLMError(f"Gemini returned no candidates: {str(out)[:200]}")
        parts = candidates[0].get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        try:
            data = first_json_object(text)
        except (json.JSONDecodeError, LLMError) as exc:
            raise LLMError(f"Reply was not JSON: {text[:120]!r}") from exc
        meta = out.get("usageMetadata", {})
        usage = Usage(
            calls=1,
            input_tokens=meta.get("promptTokenCount", 0),
            output_tokens=meta.get("candidatesTokenCount", 0) + meta.get("thoughtsTokenCount", 0),
        )
        return data, usage

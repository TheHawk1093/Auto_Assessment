"""Backend for OpenRouter (open-source and free models).

Needs OPENROUTER_API_KEY, from the environment or from `.env`. The JSON schema is given in the
prompt and the reply is parsed from the first JSON object in it, since not every free model
supports forced structured output.
"""

from __future__ import annotations

import http.client
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from autograde.llm.base import LLMClient, LLMError, Usage

URL = "https://openrouter.ai/api/v1/chat/completions"
GOEDEL_URL = "https://api.goedelmachines.com/v1/chat/completions"
_RETRY_WAIT = (5, 15, 40)  # seconds to wait after a rate-limit answer


def api_key(var: str = "OPENROUTER_API_KEY") -> str:
    """Read an API key from the environment or the `.env` file.

    Args:
        var: Name of the variable that holds the key.

    Returns:
        The key.

    Raises:
        LLMError: If the key is set in neither place.
    """
    key = os.environ.get(var)
    env = Path(".env")
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith(f"{var}="):
                key = line.split("=", 1)[1].strip().strip("\"'")
    if not key:
        raise LLMError(f"Set {var} in the environment or in .env")
    return key


def first_json_object(text: str) -> dict:
    """The first JSON object in `text`, which may be wrapped in prose or a code fence."""
    start = text.find("{")
    if start < 0:
        raise LLMError("No JSON object in the reply")
    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    return obj


class OpenRouterClient(LLMClient):
    """Chat-completions client; subclasses change `url`, `key_var` and `prefix`."""

    url = URL
    key_var = "OPENROUTER_API_KEY"
    prefix = "openrouter"

    def __init__(self, model: str, timeout_s: int = 240, retries: int = 2) -> None:
        """Load the API key for this backend."""
        super().__init__(retries)
        self.model = model
        self.timeout_s = timeout_s
        self._key = api_key(self.key_var)

    @property
    def name(self) -> str:
        """Cache label with the model id made filename-safe."""
        return f"{self.prefix}-{self.model.replace('/', '_').replace(':', '_')}"

    def _post(self, body: dict) -> dict:
        req = urllib.request.Request(
            self.url,
            json.dumps(body).encode(),
            {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"},
        )
        for wait in (*_RETRY_WAIT, None):
            try:
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    return json.load(resp)
            except urllib.error.HTTPError as exc:
                if exc.code == 429 and wait is not None:
                    time.sleep(wait)
                    continue
                raise LLMError(f"{self.prefix} HTTP {exc.code}: {exc.read()[:200]!r}") from exc
            except (
                urllib.error.URLError,
                TimeoutError,
                ConnectionError,
                http.client.HTTPException,  # a reply cut off part-way (IncompleteRead)
            ) as exc:
                raise LLMError(f"{self.prefix} request failed: {exc}") from exc
        raise LLMError("unreachable")

    def _complete(self, system: str, user: str, schema: dict) -> tuple[dict, Usage]:
        fmt = (
            "Reply with one JSON object only, no other text, matching this JSON schema:\n"
            + json.dumps(schema)
        )
        out = self._post(
            {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": f"{system}\n\n{fmt}"},
                    {"role": "user", "content": user},
                ],
                "temperature": 0,
            }
        )
        try:
            text = out["choices"][0]["message"].get("content") or ""
        except (KeyError, IndexError) as exc:
            raise LLMError(f"Unexpected reply: {str(out)[:200]}") from exc
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.S)
        try:
            data = first_json_object(text)
        except (json.JSONDecodeError, LLMError) as exc:
            raise LLMError(f"Reply was not JSON: {text[:120]!r}") from exc
        u = out.get("usage", {})
        usage = Usage(
            calls=1,
            input_tokens=u.get("prompt_tokens", 0),
            output_tokens=u.get("completion_tokens", 0),
            cost_usd=float(u.get("cost", 0) or 0),
        )
        return data, usage


class GoedelClient(OpenRouterClient):
    """Goedel Machines serves an OpenAI-compatible API; same request and reply shape."""

    url = GOEDEL_URL
    key_var = "GOEDEL_API_KEY"
    prefix = "goedel"

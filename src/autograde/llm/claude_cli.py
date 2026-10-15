"""Backend that runs prompts through the local Claude Code CLI (`claude -p`).

Uses your existing Claude login, so no API key is needed. Intended for early testing:
each call starts a process, so it is slower than the API. Tools are disabled and the
call runs from a temp directory so project files and settings never leak into the prompt.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile

from autograde.llm.base import LLMClient, LLMError, Usage


class ClaudeCLIClient(LLMClient):
    def __init__(self, model: str = "sonnet", timeout_s: int = 240, retries: int = 2) -> None:
        super().__init__(retries)
        self.model = model
        self.timeout_s = timeout_s
        self._exe = shutil.which("claude")
        if self._exe is None:
            raise LLMError("The `claude` CLI was not found on PATH.")
        self._cwd = tempfile.mkdtemp(prefix="autograde-cli-")

    @property
    def name(self) -> str:
        return f"claude_cli-{self.model}"

    def _complete(self, system: str, user: str, schema: dict) -> tuple[dict, Usage]:
        cmd = [
            self._exe, "-p",
            "--output-format", "json",
            "--tools", "",
            "--no-session-persistence",
            "--model", self.model,
            "--system-prompt", system,
            "--json-schema", json.dumps(schema),
        ]  # fmt: skip
        try:
            proc = subprocess.run(
                cmd, input=user, capture_output=True, text=True, encoding="utf-8",
                timeout=self.timeout_s, cwd=self._cwd, check=False,
            )  # fmt: skip
        except subprocess.TimeoutExpired as exc:
            raise LLMError(f"claude CLI timed out after {self.timeout_s}s") from exc
        if proc.returncode != 0:
            raise LLMError(f"claude CLI exit {proc.returncode}: {proc.stderr.strip()[:300]}")
        try:
            out = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise LLMError(f"claude CLI returned non-JSON: {proc.stdout[:200]!r}") from exc
        if out.get("is_error"):
            raise LLMError(f"claude CLI error: {str(out.get('result'))[:300]}")
        data = out.get("structured_output")
        if data is None:
            try:
                data = json.loads(out.get("result", ""))
            except json.JSONDecodeError as exc:
                raise LLMError("claude CLI gave no structured output") from exc
        u = out.get("usage", {})
        usage = Usage(
            calls=1,
            input_tokens=u.get("input_tokens", 0)
            + u.get("cache_creation_input_tokens", 0)
            + u.get("cache_read_input_tokens", 0),
            output_tokens=u.get("output_tokens", 0),
            cost_usd=float(out.get("total_cost_usd", 0.0)),
        )
        return data, usage

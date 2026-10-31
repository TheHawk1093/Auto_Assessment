"""Transcribe an image of a handwritten answer with Claude vision.

Claude CLI backend: images cannot be sent as message content (`ClaudeCLIClient` turns tools
off and takes text only). A probe showed that `claude -p --tools Read --add-dir <dir>` lets the
model open an image by path and read it, so this module makes its own CLI call with only the
Read tool, run from the image's folder. Anthropic backend: the image is sent as a base64
image block. Both return plain text in which unreadable words are marked [?word?].
"""

from __future__ import annotations

import base64
import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from autograde import prompts
from autograde.llm.base import LLMClient, LLMError, Usage

MEDIA = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
UNSURE = re.compile(r"\[\?([^\]?]*)\??\]")


@dataclass
class Transcript:
    """A transcription and the spans the reader marked unsure."""

    text: str
    low_confidence: list[str] = field(default_factory=list)


def parse(raw: str) -> Transcript:
    """Split the model reply into text and the spans it marked unsure."""
    text = raw.strip()
    return Transcript(text, [m.group(1).strip() or "?" for m in UNSURE.finditer(text)])


def cli_read(paths: list[Path], client: LLMClient, system: str, user: str) -> tuple[str, Usage]:
    """One CLI call in which the model may open the given image files with the Read tool."""
    folders = list(dict.fromkeys(str(p.resolve().parent) for p in paths))
    cmd = [client._exe, "-p", "--output-format", "json", "--tools", "Read"]
    for folder in folders:
        cmd += ["--add-dir", folder]
    cmd += ["--no-session-persistence", "--model", client.model, "--system-prompt", system]
    if client.effort:
        cmd += ["--effort", client.effort]
    try:
        proc = subprocess.run(
            cmd, input=user, capture_output=True, text=True, encoding="utf-8",
            timeout=client.timeout_s, cwd=folders[0], check=False,
        )  # fmt: skip
        out = json.loads(proc.stdout)
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        raise LLMError(f"claude CLI transcription failed: {exc}") from exc
    if proc.returncode != 0 or out.get("is_error"):
        raise LLMError(f"claude CLI error: {str(out.get('result'))[:300]}")
    u = out.get("usage", {})
    usage = Usage(
        calls=1,
        input_tokens=u.get("input_tokens", 0)
        + u.get("cache_creation_input_tokens", 0)
        + u.get("cache_read_input_tokens", 0),
        output_tokens=u.get("output_tokens", 0),
        cost_usd=float(out.get("total_cost_usd", 0.0)),
    )
    return out.get("result", ""), usage


def _api(path: Path, client: LLMClient) -> tuple[str, Usage]:
    media = MEDIA.get(path.suffix.lower())
    if media is None:
        raise LLMError(f"Unsupported image type {path.suffix!r}")
    data = base64.standard_b64encode(path.read_bytes()).decode()
    try:
        resp = client._client.messages.create(
            model=client.model, max_tokens=client.max_tokens,
            system=prompts.system("ocr.transcribe"),
            messages=[{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media, "data": data}},
                {"type": "text", "text": "Transcribe the handwritten answer."},
            ]}],
        )  # fmt: skip
    except client._anthropic.APIError as exc:
        raise LLMError(f"Anthropic API error: {exc}") from exc
    text = "".join(b.text for b in resp.content if b.type == "text")
    return text, Usage(1, resp.usage.input_tokens, resp.usage.output_tokens)


def transcribe(image_path: str | Path, client: LLMClient) -> Transcript:
    """Read a handwritten answer image; `client` is a ClaudeCLIClient or AnthropicClient."""
    path = Path(image_path)
    if not path.is_file():
        raise FileNotFoundError(path)
    if hasattr(client, "_exe"):
        text, usage = cli_read(
            [path],
            client,
            prompts.system("ocr.transcribe"),
            f"Transcribe the handwritten answer in the image file {path.resolve()}.",
        )
    elif hasattr(client, "_anthropic"):
        text, usage = _api(path, client)
    else:
        raise LLMError(f"{type(client).__name__} cannot read images")
    with client._lock:
        client.usage.add(usage)
    return parse(text)

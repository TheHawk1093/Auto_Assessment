"""Read answer-sheet photos with free hosted vision models (Gemini free tier, OpenRouter `:free`).

Only models that cost nothing are allowed. Gemini: an allow-list taken from Google's pricing page
(free-tier models). OpenRouter: the id must end in `:free` and its listed price must be zero.
Anything else raises before a request is made. API keys come from the environment or the
git-ignored `.env`, travel in headers (never in a URL) and are never logged.

Images should be header-redacted copies (tools/ocr/redact_headers.py): free tiers may keep the data.
"""

from __future__ import annotations

import base64
import http.client
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from autograde import prompts
from autograde.llm.base import LLMError
from autograde.ocr.sheets import Sheet, SheetItem, parse_sheet
from autograde.ocr.transcribe import MEDIA

ROOT = Path(__file__).resolve().parents[3]

# Free-tier models on ai.google.dev/gemini-api/docs/pricing. "-latest" aliases and Pro are left out.
GEMINI_FREE = {
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemma-4-31b-it",
    "gemma-4-26b-a4b-it",
}
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODELS = "https://openrouter.ai/api/v1/models"

_free_prices: dict[str, bool] | None = None
OPENROUTER_CAP_USD = 1.0  # free models should cost nothing; stray costs up to this are tolerated
_spent = {"usd": 0.0}
BODHAN_URL = "https://api.bodhan.ai/v1/chat/completions"
BODHAN_RUPEES_PER_IMAGE = 0.20  # the only paid reader; a per-run cap keeps a mistake cheap
BODHAN_CAP_RUPEES = 30.0
_bodhan_spent = {"images": 0}


def _key(name: str) -> str:
    if name not in os.environ:
        env = ROOT / ".env"
        if env.exists():
            for line in env.read_text(encoding="utf-8").splitlines():
                k, _, v = line.partition("=")
                if k.strip() == name:
                    return v.strip()
    if not os.environ.get(name):
        raise LLMError(f"{name} is not set (put it in .env)")
    return os.environ[name]


def _post(url: str, headers: dict, body: dict, timeout: int = 180) -> dict:
    req = urllib.request.Request(
        url, json.dumps(body).encode(), {"Content-Type": "application/json", **headers}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.load(resp)


def _call(url: str, headers: dict, body: dict, tries: int = 4) -> dict:
    """POST with back-off on rate limits. The error text never includes the request headers."""
    for attempt in range(tries):
        try:
            out = _post(url, headers, body)
            err = out.get("error") if isinstance(out, dict) else None
            # OpenRouter can answer 200 with an upstream error inside the body
            if err and err.get("code") in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(min(20 * (attempt + 1), 60))
                continue
            return out
        except urllib.error.HTTPError as exc:
            full = exc.read().decode("utf-8", "replace")
            detail = full[:300]
            if exc.code == 429 and "PerDay" in full:  # waiting a minute will not bring it back
                raise LLMError(f"HTTP 429: daily quota used up. {detail}") from None
            if exc.code in (429, 500, 502, 503, 504) and attempt < tries - 1:
                time.sleep(min(20 * (attempt + 1), 60))
                continue
            raise LLMError(f"HTTP {exc.code}: {detail}") from None
        except (
            urllib.error.URLError,
            TimeoutError,
            ConnectionError,
            http.client.HTTPException,  # the server dropped or cut off the reply
        ) as exc:
            if attempt < tries - 1:
                time.sleep(10)
                continue
            raise LLMError(f"network error: {exc}") from None
    raise LLMError("unreachable")


def _image_b64(path: Path) -> tuple[str, str]:
    media = MEDIA.get(path.suffix.lower())
    if media is None:
        raise LLMError(f"Unsupported image type {path.suffix!r}")
    return media, base64.standard_b64encode(path.read_bytes()).decode()


def gemini(pages: list[Path], model: str, system: str, user: str) -> str:
    """Read page images with a Gemini model on the free-tier allow-list and return the text."""
    if model not in GEMINI_FREE:
        raise LLMError(f"{model!r} is not on the free-tier allow-list: {sorted(GEMINI_FREE)}")
    parts: list[dict] = [{"text": user}]
    for p in pages:
        media, data = _image_b64(p)
        parts.append({"inline_data": {"mime_type": media, "data": data}})
    body = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"temperature": 0, "maxOutputTokens": 8192},
    }
    out = _call(GEMINI_URL.format(model=model), {"x-goog-api-key": _key("GEMINI_API_KEY")}, body)
    cands = out.get("candidates") or []
    if not cands:
        raise LLMError(f"Gemini returned no candidates: {str(out)[:200]}")
    texts = [
        x["text"] for x in cands[0].get("content", {}).get("parts", []) if not x.get("thought")
    ]
    return "".join(texts)


def _assert_openrouter_free(model: str) -> None:
    global _free_prices
    if not model.endswith(":free"):
        raise LLMError(f"{model!r} does not end in ':free'; only free models are allowed")
    if _free_prices is None:
        with urllib.request.urlopen(OPENROUTER_MODELS, timeout=60) as resp:
            data = json.load(resp)["data"]
        _free_prices = {
            m["id"]: float(m["pricing"].get("prompt", 1)) == 0
            and float(m["pricing"].get("completion", 1)) == 0
            for m in data
        }
    if not _free_prices.get(model):
        raise LLMError(f"{model!r} is not listed with zero price on OpenRouter")


def openrouter(pages: list[Path], model: str, system: str, user: str) -> str:
    """Read page images with a free OpenRouter model and return the text."""
    _assert_openrouter_free(model)
    content: list[dict] = [{"type": "text", "text": user}]
    for p in pages:
        media, data = _image_b64(p)
        content.append({"type": "image_url", "image_url": {"url": f"data:{media};base64,{data}"}})
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": content}],
        "temperature": 0,
        "max_tokens": 24000,  # reasoning models spend much of this on thinking before they answer
    }
    out = _call(OPENROUTER_URL, {"Authorization": "Bearer " + _key("OPENROUTER_API_KEY")}, body)
    _spent["usd"] += float((out.get("usage") or {}).get("cost") or 0)
    if _spent["usd"] > OPENROUTER_CAP_USD:
        raise LLMError(f"OpenRouter spend this run passed ${OPENROUTER_CAP_USD:.2f}; stopping")
    choices = out.get("choices") or []
    if not choices:
        raise LLMError(f"OpenRouter returned no choices: {str(out)[:200]}")
    return choices[0].get("message", {}).get("content") or ""


def bodhan(pages: list[Path], model: str, system: str, user: str) -> str:
    """Read page images with Bodhan AI IndicOCR (paid, ₹0.20 per image).

    It is called through its OpenAI-compatible API. It is a document parser, so it gets the
    images and a one-line request, not our exam-sheet prompt.
    """
    _bodhan_spent["images"] += len(pages)
    if _bodhan_spent["images"] * BODHAN_RUPEES_PER_IMAGE > BODHAN_CAP_RUPEES:
        raise LLMError(f"Bodhan spend this run passed ₹{BODHAN_CAP_RUPEES:.0f}; stopping")
    content: list[dict] = [{"type": "text", "text": "Transcribe all the text in this image."}]
    for p in pages:
        media, data = _image_b64(p)
        content.append({"type": "image_url", "image_url": {"url": f"data:{media};base64,{data}"}})
    body = {"model": model, "messages": [{"role": "user", "content": content}], "temperature": 0}
    out = _call(BODHAN_URL, {"Authorization": "Bearer " + _key("INDIC_OCR_API_KEY")}, body)
    choices = out.get("choices") or []
    if not choices:
        raise LLMError(f"Bodhan returned no choices: {str(out)[:200]}")
    return choices[0].get("message", {}).get("content") or ""


PROVIDERS = {"gemini": gemini, "openrouter": openrouter, "bodhan": bodhan}


def extract_sheet_hosted(
    name: str, pages: list[Path], provider: str, model: str, plain: bool = False
) -> Sheet:
    """Same job and prompt as `extract_sheet`, with a free hosted model. One retry on bad JSON.

    With `plain`, a short transcription prompt is used instead and the whole page text comes back
    as one item: cheaper and quicker for slow reasoning models, but without the question split.
    """
    if plain:
        text = PROVIDERS[provider](
            pages, model, prompts.system("ocr.transcribe"), "Transcribe the handwriting."
        )
        item = SheetItem(question_id="page", student_answer=text.strip())
        return Sheet(sheet=name, pages=[p.name for p in pages], items=[item])
    files = "\n".join(f"Image {i} is page {i} of the sheet." for i in range(1, len(pages) + 1))
    user = f"The sheet has {len(pages)} page image(s) attached, in order.\n{files}"
    last: LLMError | None = None
    for _ in range(2):
        text = PROVIDERS[provider](pages, model, prompts.system("ocr.sheet"), user)
        try:
            sheet = parse_sheet(text)
        except LLMError as exc:
            last = exc
            continue
        sheet.sheet, sheet.pages = name, [p.name for p in pages]
        return sheet
    raise last or LLMError("Sheet extraction failed")

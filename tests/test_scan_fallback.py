"""`autograde scan` tries the main reader first and falls back in order; paid readers are capped."""

import argparse
import json

import pytest

from autograde.cli import scan
from autograde.config import OcrConfig, ReaderConfig, Settings
from autograde.llm.base import LLMError
from autograde.ocr import hosted

CLEAN = "Name: Asha\nRoll No: S1\n\nQ1. the answer is clear and complete in every detail here"
DOUBTFUL = "Name: Asha\nRoll No: S1\n\nQ1. [?a?] [?b?] [?c?] [?d?] fine"  # most words are unsure
EVEN_WORSE = "Name: Asha\nRoll No: S1\n\nQ1. [?a?] [?b?] [?c?] [?d?] [?e?]"


def _settings(*models: str) -> Settings:
    specs = [ReaderConfig(provider="openrouter", model=m) for m in models]
    return Settings(ocr=OcrConfig(reader=specs[0], fallbacks=specs[1:]))


def _run(tmp_path, monkeypatch, settings, replies):
    """Scan one page; `replies` maps a model name to the text it returns, or to an Exception."""
    pages = tmp_path / "pages"
    pages.mkdir()
    (pages / "S1.png").write_bytes(b"\x89PNG")
    tried = []

    def fake_read(_pages, provider, model, _paper, _effort):
        tried.append(model)
        reply = replies[model]
        if isinstance(reply, Exception):
            raise reply
        return reply

    monkeypatch.setattr(scan, "read_answer_sheet", fake_read)
    args = argparse.Namespace(
        provider=None, model=None, paper=None, identities=None, folder=pages,
        out=tmp_path / "out", per_page=True, summary=None, effort=None,
    )  # fmt: skip
    scan.cmd_scan(args, settings)
    info = json.loads((tmp_path / "out" / "scan.json").read_text(encoding="utf-8"))["S1"]
    return tried, info


def test_a_clean_read_by_the_main_reader_stops_there(tmp_path, monkeypatch):
    tried, info = _run(tmp_path, monkeypatch, _settings("main", "backup"),
                       {"main": CLEAN, "backup": CLEAN})  # fmt: skip
    assert tried == ["main"] and info["reader"] == "openrouter:main" and "degraded" not in info


def test_a_failing_reader_falls_back_to_the_next(tmp_path, monkeypatch):
    tried, info = _run(tmp_path, monkeypatch, _settings("main", "backup"),
                       {"main": LLMError("rate limited"), "backup": CLEAN})  # fmt: skip
    assert tried == ["main", "backup"] and info["reader"] == "openrouter:backup"


def test_a_doubtful_read_falls_back_to_the_next_reader(tmp_path, monkeypatch):
    tried, info = _run(tmp_path, monkeypatch, _settings("main", "backup"),
                       {"main": DOUBTFUL, "backup": CLEAN})  # fmt: skip
    assert tried == ["main", "backup"] and info["reader"] == "openrouter:backup"
    assert "degraded" not in info


def test_when_no_reader_is_clean_the_least_doubtful_read_is_kept_and_marked(tmp_path, monkeypatch):
    tried, info = _run(tmp_path, monkeypatch, _settings("main", "backup"),
                       {"main": EVEN_WORSE, "backup": DOUBTFUL})  # fmt: skip
    assert tried == ["main", "backup"]
    assert info["reader"] == "openrouter:backup" and info["degraded"] == ["uncertain"]


def test_a_fallback_equal_to_the_main_reader_is_not_tried_twice(tmp_path, monkeypatch):
    tried, _ = _run(tmp_path, monkeypatch, _settings("main", "main", "backup"),
                    {"main": DOUBTFUL, "backup": CLEAN})  # fmt: skip
    assert tried == ["main", "backup"]


def test_a_repeating_reader_is_a_doubtful_read():
    stuck = " ".join(["same"] * 30 + ["other"] * 2)
    assert scan.read_problems(stuck) == ["repeating"]
    assert scan.read_problems(CLEAN) == []


def _fake_reply(cost: float):
    return lambda *a, **k: {
        "choices": [{"message": {"content": "text"}}], "usage": {"cost": cost},
    }  # fmt: skip


def test_a_paid_openrouter_model_is_allowed_but_the_spend_cap_stops_a_run(monkeypatch, tmp_path):
    page = tmp_path / "p.png"
    page.write_bytes(b"\x89PNG")
    monkeypatch.setattr(hosted, "_key", lambda name: "k")
    monkeypatch.setattr(hosted, "_spent", {"usd": 0.0})
    monkeypatch.setattr(hosted, "_call", _fake_reply(0.40))
    assert hosted.openrouter([page], "google/gemini-3.1-flash-lite", "s", "u") == "text"
    with pytest.raises(LLMError, match="spend"):
        for _ in range(3):  # 0.40 + 0.40 + 0.40 passes the $1.00 cap
            hosted.openrouter([page], "google/gemini-3.1-flash-lite", "s", "u")


def test_a_free_model_must_really_be_listed_at_zero_price(monkeypatch, tmp_path):
    page = tmp_path / "p.png"
    page.write_bytes(b"\x89PNG")
    monkeypatch.setattr(hosted, "_key", lambda name: "k")
    monkeypatch.setattr(hosted, "_free_prices", {"vendor/model:free": False})
    with pytest.raises(LLMError, match="zero price"):
        hosted.openrouter([page], "vendor/model:free", "s", "u")

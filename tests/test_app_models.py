"""The AI model catalogue: what teachers may pick, and the config a run is given."""

from __future__ import annotations

import pytest
import yaml
from streamlit.testing.v1 import AppTest

from app import config
from app.services import auth, jobs, models, overview, storage

MAIN = str(config.ROOT / "app" / "main.py")


@pytest.fixture(autouse=True)
def model_env(env, monkeypatch):
    """Admin choices in a temp file; pretend the Claude CLI and the Goedel key are present."""
    monkeypatch.setattr(models, "PATH", env / "models.json")
    monkeypatch.setattr(models.shutil, "which", lambda _: "claude")
    monkeypatch.setattr(models, "_has_key", lambda var: var == "GOEDEL_API_KEY")


def ids(options):
    return [o.id for o in options]


def ready_exam(owner: str = "t1") -> str:
    eid = storage.create_exam("Quiz", owner=owner)
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(eid, "answers", [("a.md", b"a")], False, set())
    return eid


def test_openrouter_is_locked_until_the_admin_enables_it():
    usable = ids(models.usable())
    assert "deepseek-flash" in usable and "claude-sonnet" in usable
    assert not {"or-claude-sonnet", "or-deepseek"} & set(usable)
    ok, why = models.availability(models.get("or-deepseek"))
    assert not ok and "OpenRouter is switched off" in why


def test_enabling_openrouter_still_needs_its_key(monkeypatch):
    models.set_enabled("or-deepseek", True, by="admin")
    ok, why = models.availability(models.get("or-deepseek"))
    assert not ok and "OPENROUTER_API_KEY" in why  # on, but nothing to pay with
    monkeypatch.setattr(models, "_has_key", lambda var: True)
    assert models.availability(models.get("or-deepseek"))[0]


def test_admin_can_switch_a_model_off_and_edit_an_openrouter_id():
    models.set_enabled("claude-opus", False, by="admin")
    assert "claude-opus" not in ids(models.usable())
    models.set_model_id("or-deepseek", "deepseek/other-model", by="admin")
    assert models.get("or-deepseek").model == "deepseek/other-model"


def test_missing_cli_or_key_hides_the_option(monkeypatch):
    monkeypatch.setattr(models.shutil, "which", lambda _: None)
    assert not any(o.needs == "claude" for o in models.usable())
    assert "deepseek-flash" in ids(models.usable())
    monkeypatch.setattr(models, "_has_key", lambda var: False)
    assert models.usable() == []


def test_exam_config_changes_only_the_model_fields():
    base = yaml.safe_load((config.ROOT / config.AUTOGRADE_CONFIG).read_text(encoding="utf-8"))
    cfg = models.exam_config(models.get("claude-sonnet-careful"))
    assert cfg["llm"]["backend"] == "claude_cli"
    assert cfg["llm"]["model"] == "sonnet" and cfg["llm"]["effort"] == "high"
    assert cfg["pipeline"]["rubric_model"] == "sonnet"
    assert cfg["pipeline"]["strong_backend"] == "claude_cli"
    assert cfg["paths"] == base["paths"] and cfg["pipeline"]["max_workers"] == 4
    mixed = models.exam_config(models.get("deepseek-sonnet-schemes"))
    assert mixed["llm"]["backend"] == "goedel" and mixed["pipeline"]["rubric_model"] == "sonnet"
    assert mixed["pipeline"]["strong_backend"] == "claude_cli"
    assert "effort" not in models.exam_config(models.get("deepseek-flash"))["llm"]


def test_each_exam_runs_with_its_own_model():
    eid = ready_exam()
    assert storage.load_meta(eid)["model"] == models.DEFAULT
    storage.set_model(eid, "claude-haiku")
    cmd = jobs.build_command(eid, schemes_only=False)
    with open(cmd[cmd.index("--config") + 1], encoding="utf-8") as f:
        written = yaml.safe_load(f)
    assert written["llm"]["model"] == "haiku" and written["llm"]["effort"] == "low"


def test_a_disabled_model_cannot_start_a_job():
    eid = ready_exam()
    storage.set_model(eid, "or-claude-sonnet")  # e.g. chosen before the admin locked it
    with pytest.raises(RuntimeError, match="cannot be used"):
        jobs.start(eid, schemes_only=True)
    assert not jobs.job_state(eid)  # nothing was started


def test_overview_names_the_model():
    eid = storage.create_exam("Quiz", owner="t1")
    storage.set_model(eid, "claude-opus")
    card = overview.for_owner("t1")[0]
    assert card["model"] == "Claude Opus" and card["status"] == "draft" and card["pending"] == 0


def test_settings_tab_offers_only_usable_models_and_saves_the_choice():
    auth.create_user("t1", "teacher", "T", "teacher-pass")
    eid = storage.create_exam("Quiz", owner="t1")
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = {"username": "t1", "role": "teacher", "name": ""}
    at.session_state["exam_id"] = eid
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    box = at.selectbox(key=f"model_{eid}")
    assert "Claude Sonnet via OpenRouter" not in box.options and "Claude Sonnet" in box.options
    box.select("claude-haiku").run()
    at.button(key=f"use_model_{eid}").click().run()
    assert storage.load_meta(eid)["model"] == "claude-haiku"


def test_admin_models_tab_saves_switches():
    auth.create_user("boss", "admin", "B", "long-password")
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = {"username": "boss", "role": "admin", "name": ""}
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    at.checkbox(key="en_claude-opus").uncheck()
    next(b for b in at.button if b.label == "Save").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert not models.is_enabled(models.get("claude-opus"))

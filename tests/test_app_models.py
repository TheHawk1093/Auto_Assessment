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
    """Admin choices in a temp file; pretend the Claude CLI and every key are present."""
    monkeypatch.setattr(models, "PATH", env / "models.json")
    monkeypatch.setattr(models.shutil, "which", lambda _: "claude")
    monkeypatch.setattr(models, "_has_key", lambda var: True)


def ids(options):
    return [o.id for o in options]


def ready_exam(owner: str = "t1") -> str:
    eid = storage.create_exam("Quiz", owner=owner)
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(eid, "answers", [("a.md", b"a")], False, set())
    return eid


def test_every_model_is_on_by_default_and_needs_its_key(monkeypatch):
    assert set(ids(models.usable())) == {o.id for o in models.CATALOGUE}
    monkeypatch.setattr(models, "_has_key", lambda var: False)
    monkeypatch.setattr(models.shutil, "which", lambda _: None)
    assert models.usable() == []
    ok, why = models.availability(models.get("deepseek-flash"))
    assert not ok and "GOEDEL_API_KEY" in why


def test_teachers_see_what_a_model_suits_and_costs_not_how_it_is_wired():
    for o in models.CATALOGUE + models.READERS:
        text = f"{o.label} {o.blurb}".lower()
        assert o.use and "cost" in o.price.lower()
        assert not {"goedel", "plan", "cli", "benchmark", "error"} & set(text.split())


def test_admin_can_switch_a_model_off_and_edit_its_id():
    models.set_enabled("claude-haiku", False, by="admin")
    assert "claude-haiku" not in ids(models.usable())
    models.set_model_id("deepseek-flash", "deepseek/other-model", by="admin")
    assert models.get("deepseek-flash").model == "deepseek/other-model"


def test_bodhan_is_a_reader_and_needs_its_own_key(monkeypatch):
    bodhan = models.get_reader("bodhan")
    assert bodhan.provider == "bodhan" and models.reader_availability(bodhan)[0]
    monkeypatch.setattr(models, "_has_key", lambda var: var != "INDIC_OCR_API_KEY")
    ok, why = models.reader_availability(bodhan)
    assert not ok and "INDIC_OCR_API_KEY" in why


def test_exam_config_changes_only_the_model_fields():
    base = yaml.safe_load((config.ROOT / config.AUTOGRADE_CONFIG).read_text(encoding="utf-8"))
    cfg = models.exam_config(models.get("claude-haiku"))
    assert cfg["llm"]["backend"] == "claude_cli"
    assert cfg["llm"]["model"] == "haiku" and cfg["llm"]["effort"] == "low"
    assert cfg["pipeline"]["rubric_model"] == "haiku"
    assert cfg["pipeline"]["strong_backend"] == "claude_cli"
    assert cfg["paths"] == base["paths"] and cfg["pipeline"]["max_workers"] == 4
    mixed = models.exam_config(models.get("deepseek-haiku-schemes"))
    assert mixed["llm"]["backend"] == "goedel" and mixed["pipeline"]["rubric_model"] == "haiku"
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
    storage.set_model(eid, "claude-haiku")
    models.set_enabled("claude-haiku", False, by="admin")
    with pytest.raises(RuntimeError, match="cannot be used"):
        jobs.start(eid, schemes_only=True)
    assert not jobs.job_state(eid)  # nothing was started


def test_overview_names_the_model_and_the_kind():
    eid = storage.create_exam("Quiz", owner="t1")
    storage.create_exam("Homework", owner="t1", kind="assignment")
    storage.set_model(eid, "claude-haiku")
    cards = {c["title"]: c for c in overview.for_owner("t1")}
    assert cards["Quiz"]["model"] == "Claude Haiku" and cards["Quiz"]["kind"] == "exam"
    assert cards["Homework"]["kind"] == "assignment"


def test_settings_tab_offers_usable_models_and_saves_the_choice():
    auth.create_user("t1", "teacher", "T", "teacher-pass")
    eid = storage.create_exam("Quiz", owner="t1")
    models.set_enabled("deepseek-haiku-schemes", False, by="admin")
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = {"username": "t1", "role": "teacher", "name": ""}
    at.session_state["exam_id"] = eid
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    box = at.selectbox(key=f"model_{eid}")
    assert "deepseek-haiku-schemes" not in box.options and "Claude Haiku" in box.options
    box.select("claude-haiku").run()
    at.button(key=f"use_model_{eid}").click().run()
    assert storage.load_meta(eid)["model"] == "claude-haiku"


def test_admin_models_tab_saves_switches():
    auth.create_user("boss", "admin", "B", "long-password")
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = {"username": "boss", "role": "admin", "name": ""}
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    at.checkbox(key="en_deepseek-haiku-schemes").uncheck()
    next(b for b in at.button if b.label == "Save").click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert not models.is_enabled(models.get("deepseek-haiku-schemes"))

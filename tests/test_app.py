"""The web app: services (storage, settings, jobs, text) and a headless run of every page.

No network and no marking: the pages are driven with Streamlit's AppTest over a fabricated run.
"""

from __future__ import annotations

import io
import json
import os
import zipfile
from datetime import datetime, timedelta

import pytest
from streamlit.testing.v1 import AppTest

from app import config, text
from app.services import auth, jobs, settings_spec, storage
from app_support import fabricate_run

MAIN = str(config.ROOT / "app" / "main.py")


def make_zip(entries: dict[str, str]) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, body in entries.items():
            z.writestr(name, body)
    return buf.getvalue()


# ---------- text ----------


def test_normalize_composes_and_keeps_joiners():
    assert text.normalize("é") == "é"
    assert text.normalize("﻿hi\x00") == "hi"
    assert text.normalize("क्‍ष") == "क्‍ष"  # ZWJ changes the glyph, so it stays
    assert text.normalize("a\tb\nc") == "a\tb\nc"


def test_for_markdown_converts_latex_delimiters():
    assert text.for_markdown(r"so \(x^2\) and \[y=1\]") == "so $x^2$ and $$y=1$$"
    assert text.for_markdown("price $5") == "price $5"


# ---------- storage ----------


def test_zip_is_flattened_and_cannot_escape(env):
    eid = storage.create_exam("Quiz")
    data = make_zip(
        {
            "folder/a.md": "A",
            "../evil.txt": "x",
            "b.exe": "x",
            "__MACOSX/c.md": "x",
            ".hidden.md": "x",
        }
    )
    saved, skipped = storage.save_uploads(eid, "answers", [("s.zip", data)], True, set())
    assert sorted(saved) == ["a.md", "evil.txt"]
    assert not (env / "evil.txt").exists()
    assert {p.name for p in storage.uploaded_files(eid, "answers")} == {"a.md", "evil.txt"}
    assert any("b.exe" in s for s in skipped)


def test_file_names_are_normalised(env):
    eid = storage.create_exam("Quiz")
    nfd = "résumé.md"
    storage.save_uploads(eid, "answers", [(nfd, b"x")], False, set())
    assert storage.uploaded_files(eid, "answers")[0].name == "résumé.md"


def test_bad_zip_and_wrong_type_are_skipped_not_fatal(env):
    eid = storage.create_exam("Quiz")
    saved, skipped = storage.save_uploads(
        eid, "answers", [("x.zip", b"not a zip"), ("y.exe", b"x")], True, set()
    )
    assert saved == [] and len(skipped) == 2


def test_status_follows_the_files_and_run(env):
    eid = storage.create_exam("Quiz")
    assert storage.exam_status(eid) == "draft"
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(eid, "answers", [("a.md", b"q")], False, set())
    assert storage.exam_status(eid) == "ready"
    storage.run_path(eid).mkdir(parents=True)
    (storage.run_path(eid) / "intake.json").write_text("{}")
    assert storage.exam_status(eid) == "prepared"
    (storage.run_path(eid) / "marks.csv").write_text("student\n")
    assert storage.exam_status(eid) == "marked"
    storage.delete_exam(eid)
    assert not storage.list_exams() and not storage.run_path(eid).exists()


# ---------- settings and command ----------


def test_default_settings_add_no_flags():
    assert settings_spec.cli_args(settings_spec.defaults()) == []


def test_settings_become_flags():
    s = settings_spec.defaults() | {
        "granularity": "half",
        "mark_step": 0.5,
        "count_best": 3,
        "note": "units needed",
        "question_notes": {"2a": "either method", "2b": "  "},
        "struck_out": ["S4=3", "S5=1"],
        "working_required": True,
    }
    args = settings_spec.cli_args(s)
    assert args[:4] == ["--granularity", "half", "--mark-step", "0.5"]
    assert args[args.index("--count-best") :][:2] == ["--count-best", "3"]
    assert args.count("--struck-out") == 2 and "S5=1" in args
    assert "2a=either method" in args and not any(a.startswith("2b=") for a in args)
    assert "--working-required" in args and "--no-follow-through" not in args


def test_every_field_has_a_widget_kind_and_a_real_cli_flag():
    from autograde.cli import _parser

    sub = next(a for a in _parser()._actions if a.dest == "cmd")
    known = set(sub.choices["exam"]._option_string_actions)
    assert {f.flag for f in settings_spec.FIELDS} <= known


def test_build_command(env):
    eid = storage.create_exam("Quiz")
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(eid, "reference", [("r.md", b"r")], True, set())
    storage.save_uploads(eid, "answers", [("a.md", b"a"), ("roster.csv", b"x")], False, {".csv"})
    storage.update_settings(eid, strictness="strict")
    cmd = jobs.build_command(eid, schemes_only=True)
    assert cmd[cmd.index("--name") + 1] == f"app_{eid}"
    assert cmd[cmd.index("--strictness") + 1] == "strict" and cmd[-1] == "--schemes-only"
    assert cmd[cmd.index("--answers") + 1].endswith("answers")
    assert "--reference" in cmd


# ---------- jobs ----------


def write_job(eid: str, **state) -> None:
    base = {
        "kind": "mark",
        "state": "running",
        "started": datetime.now().isoformat(timespec="seconds"),
    }
    (storage.exam_dir(eid) / "job.json").write_text(json.dumps(base | state))


def test_dead_process_is_reported_as_failed(env):
    eid = storage.create_exam("Quiz")
    write_job(eid, pid=2**22 + 12345)  # no such process
    assert jobs.job_state(eid)["state"] == "failed"
    assert jobs.running_exam() is None


def test_live_process_stays_running_and_blocks_a_second_job(env):
    eid = storage.create_exam("Quiz")
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(eid, "answers", [("a.md", b"q")], False, set())
    write_job(eid, pid=os.getpid())
    assert jobs.job_state(eid)["state"] == "running"
    with pytest.raises(RuntimeError, match="Another job"):
        jobs.start(eid, schemes_only=True)


def test_start_without_files_is_refused(env):
    eid = storage.create_exam("Quiz")
    with pytest.raises(RuntimeError, match="Upload"):
        jobs.start(eid, schemes_only=True)


def test_job_that_never_reported_a_process_goes_stale(env):
    eid = storage.create_exam("Quiz")
    old = (datetime.now() - timedelta(seconds=config.STALE_START_S + 5)).isoformat(
        timespec="seconds"
    )
    write_job(eid, started=old)
    assert jobs.job_state(eid)["state"] == "failed"


# ---------- pages ----------


def test_teacher_page_renders_every_tab(env):
    eid = storage.create_exam("Quiz", owner="t1")
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(eid, "answers", [("a.md", b"a")], False, set())
    fabricate_run(eid)
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = {"username": "t1", "role": "teacher", "name": "T"}
    at.session_state["exam_id"] = eid
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    tabs = [t.label for t in at.tabs]
    assert [t.split(": ")[-1] for t in tabs] == [
        "Upload", "Settings", "Mark", "Results", "Publish", "Regrades",
    ]  # fmt: skip
    assert {"Questions", "Students", "Average", "To check"} <= {m.label for m in at.metric}


def test_login_screen_and_first_admin_setup(env):
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.run()
    assert not at.exception and "Create administrator" in [b.label for b in at.button]
    at.text_input[0].set_value("boss")
    at.text_input[2].set_value("a-long-password")
    at.button[0].click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert auth.authenticate("boss", "a-long-password")["role"] == "admin"
    assert at.session_state["user"]["username"] == "boss"


def test_admin_and_empty_student_pages_render(env):
    auth.create_user("boss", "admin", "Boss", "a-long-password")
    auth.create_user("S1", "student", "", "a-long-password")
    for user, page in (({"username": "boss", "role": "admin", "name": ""}, "Admin"),
                       ({"username": "S1", "role": "student", "name": ""}, "Student")):  # fmt: skip
        at = AppTest.from_file(MAIN, default_timeout=60)
        at.session_state["user"] = user
        at.run()
        assert not at.exception, (page, [e.value for e in at.exception])

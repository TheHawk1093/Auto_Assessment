"""Identity in the app: the pipeline is given the student database, the messy demo sheets resolve as
designed against it, and the teacher can settle what the code could not."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from app import config
from app.services import courses, db, demo, identity, jobs, settings_spec, storage, students
from autograde.intake.answers import load_answers_identified
from autograde.intake.identity import _Claimed, _Pick, load_directories, load_directory
from autograde.intake.models import Paper, QuestionSpec
from fakes import FakeClient

A, B, C, D, E, F, G, H = demo.ROLLS
MAIN = str(config.ROOT / "app" / "main.py")
MESSY = demo.exam_id("messy")
PAPER = Paper(
    questions=[
        QuestionSpec(id=q, text="q", max_mark=5) for q in ("1", "2", "3a", "3b", "4", "5", "6")
    ]
)


@pytest.fixture
def seeded(env):
    demo.seed(app_data=env)


def directory_for(exam_id: str):
    """What the job hands the pipeline: the database, then the roster uploaded with the sheets."""
    roster_csv = [p for p in storage.uploaded_files(exam_id, "answers") if p.suffix == ".csv"]
    return load_directories([db.PATH, *roster_csv], storage.load_meta(exam_id)["course_id"])


def messy_entries(**fixes):
    people = directory_for(MESSY)
    client = FakeClient(
        {
            _Claimed: lambda _: {"roll_number": "", "name": "Student"},
            _Pick: lambda _: {"student_id": "none"},
        }
    )
    folder = demo.PIPELINE_DIR / "answers_messy"
    return load_answers_identified(folder, PAPER, client, people, fixes or None)


# ---------- the pipeline is handed the database ----------


def test_the_job_passes_the_student_database_the_course_and_the_fixes(seeded):
    cmd = jobs.build_command(MESSY, schemes_only=True)
    at = cmd.index("--directory")
    assert cmd[at + 1] == str(db.PATH) and cmd[at + 2].endswith(
        "roster.csv"
    )  # database, then roster
    course_id = storage.load_meta(MESSY)["course_id"]
    assert cmd[cmd.index("--course-id") + 1] == str(course_id)
    assert "--identity-fixes" not in cmd
    identity.set_fix(MESSY, "x.md", G)
    cmd = jobs.build_command(MESSY, schemes_only=False)
    fixes = cmd[cmd.index("--identity-fixes") + 1]
    assert json.loads(Path(fixes).read_text(encoding="utf-8")) == {"x.md": G}


def test_without_a_database_the_job_falls_back_to_file_names(env):
    eid = storage.create_exam("Quiz", owner="t1")
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(eid, "answers", [("a.md", b"a")], False, set())
    assert not db.PATH.exists()
    assert "--directory" not in jobs.build_command(eid, schemes_only=True)


def test_allow_unresolved_is_a_setting_and_a_flag():
    assert "--allow-unresolved" in settings_spec.cli_args(
        settings_spec.defaults() | {"allow_unresolved": True}
    )
    assert "--allow-unresolved" not in settings_spec.cli_args(settings_spec.defaults())


def test_the_cli_accepts_the_identity_options():
    from autograde.cli import _parser

    sub = next(a for a in _parser()._actions if a.dest == "cmd")
    known = set(sub.choices["exam"]._option_string_actions)
    assert {"--directory", "--course-id", "--identity-fixes", "--allow-unresolved"} <= known


# ---------- the messy demo sheets, against the real database ----------


def test_the_messy_exam_has_its_sheets_and_the_roster(seeded):
    names = sorted(p.name for p in storage.uploaded_files(MESSY, "answers"))
    assert "x.md" in names and "copy of S24008.md" in names and "roster.csv" in names
    assert len([n for n in names if n.endswith(".md")]) == 9
    assert storage.load_meta(MESSY)["settings"]["struck_out"] == []


def test_each_messy_sheet_resolves_as_designed(seeded):
    answers, warnings, resolutions = messy_entries()
    by_file = {r.source: r for r in resolutions}
    assert len(resolutions) == 9
    scan = by_file["scan_001.md"]
    assert (scan.student_id, scan.method, scan.status) == (A, "roll+name", "ok")
    assert (by_file["IMG_0042.md"].student_id, by_file["IMG_0042.md"].method) == (B, "name")
    assert by_file["final answer sheet.md"].student_id == C
    assert by_file["final answer sheet.md"].method == "roll_corrected"
    assert (by_file["Divya_quiz.md"].student_id, by_file["Divya_quiz.md"].status) == (D, "ok")
    assert (by_file["S24005.md"].student_id, by_file["S24005.md"].method) == (E, "filename")
    mismatch = by_file["sheet_6.md"]
    assert mismatch.student_id == F and "name_mismatch" in mismatch.flags  # the roll wins
    assert by_file["x.md"].status == "unresolved" and by_file["x.md"].student_id is None
    held = [by_file["S24008.md"], by_file["copy of S24008.md"]]
    assert {r.status for r in held} == {"unresolved"} and all(
        f"duplicate:{H}" in r.flags for r in held
    )
    assert set(answers) == {A, B, C, D, E, F}  # G and H are left for the teacher
    assert len([w for w in warnings if "could not tell" in w]) == 3  # one per held sheet


def test_the_teachers_fixes_bring_in_the_rest(seeded):
    fixes = {"x.md": G, "S24008.md": H}  # x.md is Gauri's; of the two H sheets, keep this one
    answers, _, resolutions = messy_entries(**fixes)
    status = {r.source: r.status for r in resolutions}
    assert set(answers) == set(demo.ROLLS)
    assert status["x.md"] == "ok" and status["S24008.md"] == "ok"
    assert status["copy of S24008.md"] == "unresolved"  # the other copy stays held


def test_a_student_only_in_the_roster_is_still_recognised(seeded):
    """H is not in the database until the class is enrolled, but the roster uploaded with the
    sheets names them: their sheet is not 'unknown'."""
    assert students.get(H) is None
    assert H in {p.student_id for p in directory_for(MESSY)}
    assert H not in {p.student_id for p in load_directory(db.PATH)}


def test_the_students_come_from_the_database_not_the_file_names(seeded):
    answers, _, _ = messy_entries()
    assert {students.name_of(s) for s in answers} >= {"Aarav Mehta", "Bhavna Iyer"}


def test_once_a_course_has_students_an_outsider_is_flagged(seeded):
    cid = storage.load_meta(MESSY)["course_id"]
    courses.enrol(cid, A, "teacher_1")  # now the roster has information: only A is in
    people = {p.student_id: p for p in load_directory(db.PATH, cid)}
    assert people[A].enrolled and not people[B].enrolled


# ---------- the report and the teacher's fixes ----------


def fake_report(exam_id: str, entries: list[dict]) -> None:
    run = storage.run_path(exam_id)
    run.mkdir(parents=True, exist_ok=True)
    (run / "identity.json").write_text(json.dumps(entries), encoding="utf-8")


def entry(source: str, sid: str | None, status: str, **extra) -> dict:
    base = {
        "source": source, "student_id": sid, "method": "roll", "status": status, "flags": [],
        "claimed": {"roll": sid or "", "name": ""}, "name": "", "candidates": [],
    }  # fmt: skip
    return base | extra


def test_the_report_applies_fixes_and_counts_what_still_blocks(seeded):
    fake_report(MESSY, [entry("a.md", A, "ok"), entry("b.md", None, "unresolved"),
                        entry("c.md", None, "unresolved"), entry("d.md", B, "check")])  # fmt: skip
    assert [e["source"] for e in identity.blocking(MESSY)] == ["b.md", "c.md"]
    assert [e["source"] for e in identity.needs_check(MESSY)] == ["d.md"]
    identity.set_fix(MESSY, "b.md", G)
    assert [e["source"] for e in identity.blocking(MESSY)] == ["c.md"]
    fixed = next(e for e in identity.report(MESSY) if e["source"] == "b.md")
    assert (fixed["student_id"], fixed["method"], fixed["status"]) == (G, "teacher", "ok")
    identity.clear_fix(MESSY, "b.md")
    assert len(identity.blocking(MESSY)) == 2


def test_a_fix_must_name_a_real_student(seeded):
    with pytest.raises(ValueError, match="no student"):
        identity.set_fix(MESSY, "b.md", "NOT-A-ROLL")


def test_choices_put_the_likely_candidates_first_then_the_course_then_everyone(seeded):
    cid = storage.load_meta(MESSY)["course_id"]
    courses.enrol(cid, C, "teacher_1")
    ids = [sid for sid, _ in identity.choices(MESSY, {"candidates": [{"student_id": G}]})]
    assert ids[0] == G and ids[1] == C and set(ids) >= set(demo.ROLLS[:7])
    assert len(ids) == len(set(ids))  # no one twice
    assert dict(identity.choices(MESSY))[A] == f"{A} · Aarav Mehta"


# ---------- the Mark tab ----------


def teacher_page(exam_id: str) -> AppTest:
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = {"username": "teacher_1", "role": "teacher", "name": "T"}
    at.session_state["exam_id"] = exam_id
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def mark_button(at: AppTest):
    return next(b for b in at.button if b.label == "Mark all answers")


def test_marking_is_held_while_a_sheet_is_unattributed_and_released_by_a_fix(seeded):
    fake_report(
        MESSY, [entry("a.md", A, "ok"), entry("x.md", None, "unresolved", flags=["no_identity"])]
    )
    at = teacher_page(MESSY)
    assert mark_button(at).disabled
    assert any("cannot be attributed to a student" in w.value for w in at.warning)
    assert "Who wrote which sheet" in [h.value for h in at.subheader]
    at.selectbox(key=f"who_{MESSY}_x.md").select(G).run()
    next(b for b in at.button if b.key == f"fix_{MESSY}_x.md").click().run()
    assert identity.fixes_for(MESSY) == {"x.md": G}
    assert not mark_button(teacher_page(MESSY)).disabled


def test_the_allow_setting_releases_marking_without_a_fix(seeded):
    fake_report(MESSY, [entry("x.md", None, "unresolved")])
    assert mark_button(teacher_page(MESSY)).disabled
    storage.update_settings(MESSY, allow_unresolved=True)
    assert not mark_button(teacher_page(MESSY)).disabled


def test_a_sheet_that_needs_a_check_does_not_hold_marking_but_is_shown(seeded):
    said = {"roll": "", "name": "Bhavna Iyer"}
    fake_report(
        MESSY,
        [entry("d.md", B, "check", flags=["matched_by_name"], method="name", claimed=said,
               name="Bhavna Iyer")],
    )  # fmt: skip
    at = teacher_page(MESSY)
    assert not mark_button(at).disabled
    shown = " ".join(m.value for m in at.markdown)
    assert "Please check" in shown and "Bhavna Iyer" in shown

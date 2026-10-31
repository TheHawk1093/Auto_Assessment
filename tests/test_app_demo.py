"""The test personas and demo data: the seeded scenario is complete, isolated, repeatable and
removable, the grade cards come out right for every enrolment combination, and the pipeline test
files agree with their own answer key."""

from __future__ import annotations

import re

import pytest
from streamlit.testing.v1 import AppTest

from app import config
from app.services import (
    auth,
    courses,
    demo,
    gradecard,
    grades,
    jobs,
    publishing,
    regrades,
    roster,
    storage,
    students,
)
from autograde.schemas import Item, Result

A, B, C, D, E, F, G, H = demo.ROLLS
MAIN = str(config.ROOT / "app" / "main.py")
MECH, THERMO = demo.exam_id("mech"), demo.exam_id("thermo")
CIRCUITS, LAB, PIPE = demo.exam_id("circuits"), demo.exam_id("lab"), demo.exam_id("pipeline")


@pytest.fixture
def seeded(env):
    return demo.seed(app_data=env)


def percents(student_id: str) -> dict[str, float | None]:
    card = gradecard.for_student(student_id)
    return {c["course"]["code"]: c["percent"] for c in card["courses"]}


def course_id(code: str) -> int:
    return next(c["id"] for c in courses.list_courses() if c["code"] == code)


# ---------- the accounts ----------


def test_every_persona_can_sign_in(seeded):
    assert set(seeded) == {p.username for p in demo.PERSONAS}
    for p in demo.PERSONAS:
        user = auth.authenticate(p.username, seeded[p.username])
        assert user and user["role"] == p.role
        assert user["student_id"] == (p.student_id or None)


def test_usernames_are_generic_the_admin_is_admin_admin_and_ids_are_unique(seeded):
    names = [p.username for p in demo.PERSONAS]
    assert "admin" in names and "teacher_1" in names and "teacher_2" in names
    assert [n for n in names if n.startswith("student_")] == [f"student_{c}" for c in "ABCDEFG"]
    assert auth.authenticate("admin", "admin")["role"] == "admin"
    ids = [p.student_id for p in demo.PERSONAS if p.student_id]
    assert len(set(ids)) == len(ids) == 7 and all(re.fullmatch(r"S24\d{3}", i) for i in ids)
    assert students.account_of(A) == "student_A" and students.account_of(H) is None


def test_older_named_accounts_are_replaced(env):
    auth.create_user("alice", "student", "Alice", "old-password")
    auth.create_user("teacher_rao", "teacher", "Rao", "old-password")
    demo.seed(app_data=env)
    assert not auth.exists("alice") and not auth.exists("teacher_rao")
    assert students.get("alice") is None  # the old student record went too


# ---------- courses, enrolments and exams ----------


def test_courses_belong_to_the_right_teachers_and_exams_to_courses(seeded):
    by_code = {c["code"]: c for c in courses.list_courses()}
    assert {code: c["teacher"] for code, c in by_code.items()} == {
        "ME1001": "teacher_1",
        "ME1002": "teacher_1",
        "ME1003": "teacher_1",
        "EE1001": "teacher_2",
    }
    in_course = {m["id"]: courses.get(m["course_id"])["code"] for m in storage.list_exams()}
    assert in_course[MECH] == "ME1001" and in_course[THERMO] == "ME1002"
    assert in_course[CIRCUITS] == in_course[LAB] == "EE1001" and in_course[PIPE] == "ME1003"


def test_exams_sit_at_the_stages_the_stories_say(seeded):
    status = {e["id"]: storage.exam_status(e["id"]) for e in storage.list_exams()}
    assert (status[MECH], status[CIRCUITS]) == ("published", "published")
    assert (status[THERMO], status[LAB]) == ("marked", "marked")
    assert status[demo.exam_id("fluids")] == "draft" and status[PIPE] == "ready"
    assert status[demo.exam_id("messy")] == "ready"


def test_each_teacher_sees_only_their_own_courses_and_exams(seeded):
    one = {e["id"] for e in storage.list_exams("teacher_1")}
    two = {e["id"] for e in storage.list_exams("teacher_2")}
    assert len(one) == 5 and two == {CIRCUITS, LAB} and not one & two
    assert [c["code"] for c in courses.list_courses("teacher_2")] == ["EE1001"]
    assert len(courses.list_courses("teacher_1")) == 3


# ---------- the grade card in every enrolment combination ----------


def test_a_is_with_both_teachers_and_the_card_shows_both(seeded):
    card = gradecard.for_student(A)
    assert {c["course"]["teacher"] for c in card["courses"]} == {"teacher_1", "teacher_2"}
    # Mechanics 9/10; Circuits 3/6; Thermodynamics is unpublished so has no percentage yet
    assert percents(A) == {"EE1001": 50.0, "ME1001": 90.0, "ME1002": None}
    assert card["overall_percent"] == 70.0


def test_b_and_c_are_with_teacher_1_only(seeded):
    assert set(percents(B)) == {"ME1001", "ME1002"} and set(percents(C)) == {"ME1001", "ME1002"}
    assert percents(B)["ME1001"] == 70.0  # 3 + 2 (raised from 1 after the regrade) + 2 of 10
    assert percents(C)["ME1001"] == 25.0


def test_d_is_with_teacher_2_only(seeded):
    assert percents(D) == {"EE1001": 100.0}  # Circuits Quiz 6/6; the Lab Test is unpublished
    teachers = {c["course"]["teacher"] for c in gradecard.for_student(D)["courses"]}
    assert teachers == {"teacher_2"}


def test_f_dropped_so_the_course_and_exam_vanish_but_the_marks_remain(seeded):
    assert gradecard.for_student(F)["courses"] == [] and publishing.exams_for_student(F) == []
    assert grades.final_marks(MECH)[F]["1"] == 3.5  # still marked
    courses.enrol(course_id("ME1001"), F, "teacher_1")  # re-enrolled
    assert percents(F) == {"ME1001": 95.0}  # 9.5 of 10, straight back


def test_g_was_marked_but_never_enrolled_so_sees_nothing_and_the_teacher_is_told(seeded):
    assert gradecard.for_student(G)["courses"] == []
    with pytest.raises(PermissionError):
        publishing.student_view(MECH, G)
    assert publishing.roster_problems(MECH)["not_enrolled"] == [F, G]  # F dropped, G never joined
    courses.enrol(course_id("ME1001"), G, "teacher_1")
    assert publishing.student_view(MECH, G)["total"] == 5.0


def test_publishing_thermodynamics_changes_exactly_the_students_in_that_course(seeded):
    before = {s: percents(s) for s in (A, B, C, D, E)}
    publishing.publish(THERMO, "teacher_1")
    assert percents(A)["ME1002"] == 100.0
    assert percents(B)["ME1002"] == pytest.approx(57.1, abs=0.1)
    assert percents(C)["ME1002"] == pytest.approx(21.4, abs=0.1)
    assert gradecard.for_student(A)["overall_percent"] == pytest.approx(80.0)  # mean 90, 100, 50
    assert percents(D) == before[D] and percents(E) == before[E]  # not in ME1002


def test_teacher_2_raising_a_mark_moves_only_the_circuits_percentage(seeded):
    grades.override(CIRCUITS, A, "2", 3.0, "Series was right.", by="teacher_2")
    now = percents(A)
    assert now["EE1001"] == 100.0 and now["ME1001"] == 90.0  # Mechanics untouched
    assert percents(D) == {"EE1001": 100.0}


def test_a_regrade_upheld_by_teacher_1_moves_only_the_mechanics_percentage(seeded):
    (req,) = regrades.list_requests(MECH, A, status="pending")
    regrades.decide(req["id"], upheld=True, reply="Agreed.", by="teacher_1", new_mark=3.0)
    assert percents(A)["ME1001"] == 100.0 and percents(A)["EE1001"] == 50.0


def test_regrade_scenario_a_waits_and_b_was_upheld(seeded):
    a = regrades.list_requests(MECH, A)
    assert [r["status"] for r in a] == ["pending"] and a[0]["old_mark"] == 2.0
    b = regrades.list_requests(MECH, B)
    assert [(r["status"], r["old_mark"], r["new_mark"]) for r in b] == [("upheld", 1.0, 2.0)]
    rows = publishing.student_view(MECH, B)["rows"]
    assert next(r for r in rows if r["question"] == "2")["mark_changed"]
    assert regrades.allowance(MECH, A)["left"] == 1
    assert regrades.allowance(MECH, C)["left"] == 2


def test_hindi_and_maths_reach_the_student(seeded):
    rows = publishing.student_view(MECH, E)["rows"]
    assert "परास" in rows[0]["answer"] and r"\frac{u^2" in rows[0]["answer"]


# ---------- the pipeline test exam ----------


def test_pipeline_exam_is_ready_with_real_files_in_an_empty_course(seeded):
    names = lambda section: [p.name for p in storage.uploaded_files(PIPE, section)]  # noqa: E731
    assert names("paper") == ["paper.md"]
    assert names("reference") == ["model_answer.md", "rubric.md"]
    answers = names("answers")
    assert sorted(a for a in answers if a.endswith(".md")) == [f"{r}.md" for r in demo.ROLLS]
    assert "roster.csv" in answers
    assert storage.load_meta(PIPE)["settings"]["struck_out"] == [f"{F}=6"]
    cid = storage.load_meta(PIPE)["course_id"]
    assert courses.get(cid)["code"] == "ME1003" and courses.roster(cid) == []
    cmd = jobs.build_command(PIPE, schemes_only=False)
    assert cmd[cmd.index("--struck-out") + 1] == f"{F}=6"


def test_after_marking_the_pipeline_exam_enrols_its_students_and_makes_the_missing_account(seeded):
    """Stand in for a finished run, then use the Publish tab's step: all eight students are
    enrolled, and only the one without an account (H) gets one."""
    answers = {r: demo.MECH_ANSWERS[A] for r in demo.ROLLS}
    demo._write_run(demo.DemoExam("pipeline", "x", "som", "marked", demo.MECH_Q, answers))
    rows = {r["student"]: r for r in roster.create_accounts(PIPE, by="teacher_1")}
    assert {s for s, r in rows.items() if r["status"] == "created"} == {H}
    assert all(rows[s]["status"] == "exists" for s in (A, B, C, D, E, F, G))
    assert rows[H]["name"] == demo.NAMES[H] and len(rows[H]["password"]) >= auth.MIN_PASSWORD
    cid = storage.load_meta(PIPE)["course_id"]
    assert {r["student_id"] for r in courses.roster(cid)} == set(demo.ROLLS)
    assert publishing.roster_problems(PIPE) == {"not_enrolled": [], "no_marks": []}


def test_pipeline_roster_names_all_eight_students(seeded):
    info = roster.parse_roster(roster.roster_file(PIPE).read_bytes())
    assert info[A]["name"] == "Aarav Mehta" and info[A]["email"] == "aarav.mehta@example.edu"
    assert {r: i["name"] for r, i in info.items()} == demo.NAMES
    assert len(info) == 8


def test_pipeline_files_agree_with_their_answer_key():
    """Every student has an answer file and a row in the key; every answer is labelled with the
    paper's question ids; the key never exceeds a question's marks."""
    marks = {"1": 5, "2": 5, "3a": 2, "3b": 3, "4": 5, "5": 5, "6": 5}
    paper = (demo.PIPELINE_DIR / "paper.md").read_text(encoding="utf-8")
    assert sum(marks.values()) == 30 and "best five" in paper and "no working" in paper
    expected = demo.load_expected()
    assert {s for s, _ in expected} == set(demo.ROLLS)
    for (student, q), mark in expected.items():
        assert q in marks and (mark is None or 0 <= mark <= marks[q])
        text = (demo.PIPELINE_DIR / "answers" / f"{student}.md").read_text(encoding="utf-8")
        assert re.search(rf"^Q{q}\.", text, re.M | re.I), (student, q)
    assert expected[(F, "6")] is None  # struck out: nothing to mark


def test_the_best_five_of_the_key_match_the_readme():
    expected = demo.load_expected()
    totals = {}
    for student in {s for s, _ in expected}:
        groups: dict[str, float] = {}
        for (s, q), mark in expected.items():
            if s == student and mark is not None:
                groups[q[0]] = groups.get(q[0], 0.0) + mark
        totals[student] = sum(sorted(groups.values(), reverse=True)[:5])
    assert totals == dict(zip(demo.ROLLS, [25, 20, 16.5, 3.5, 20, 13.5, 18, 24], strict=True))


def fake_run(exam: str, marks: dict[tuple[str, str], float | None]) -> None:
    """A results file with the given marks, as the pipeline would write it."""
    lines = []
    for (student, q), mark in marks.items():
        if mark is None:
            continue
        item = Item(
            id=f"x/{student}/{q}", dataset="exam", question_id=q, question="q",
            model_answer="m", student_answer="a", max_mark=5.0,
        )  # fmt: skip
        lines.append(Result(item=item, mode="pipeline", predicted_mark=mark).model_dump_json())
    run = storage.run_path(exam)
    run.mkdir(parents=True)
    (run / "results.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_compare_finds_no_gap_when_the_pipeline_matches_the_key(env):
    fake_run("x", demo.load_expected())
    rows = demo.compare("x")
    assert len(rows) == 56 and not [r for r in rows if r["off"]]


def test_compare_flags_big_gaps_and_a_question_that_should_not_be_marked(env):
    marks = dict(demo.load_expected())
    marks[(A, "1")] = 2.0  # expected 5: a gap of 3
    marks[(B, "4")] = 3.5  # expected 4: within a mark, fine
    marks[(F, "6")] = 2.0  # was struck out, so should not be marked at all
    fake_run("x", marks)
    off = {(r["student"], r["question"]) for r in demo.compare("x") if r["off"]}
    assert off == {(A, "1"), (F, "6")}
    report = demo._report(demo.compare("x"), 1.0)
    assert f"{A} Q1: expected 5, got 2" in report and f"{F} Q6: expected not marked" in report


# ---------- repeatable, documented, removable ----------


def test_seeding_twice_changes_nothing_and_keeps_passwords(env):
    first = demo.seed(app_data=env)
    second = demo.seed(app_data=env)
    assert first == second
    assert len(regrades.list_requests(MECH)) == 2  # not duplicated
    assert len(courses.list_courses()) == 4
    assert [u["username"] for u in auth.list_users(role="admin")] == ["admin"]


def test_the_sheet_lists_every_persona_ids_and_the_enrolment_map(env):
    passwords = demo.seed(app_data=env)
    sheet = (env / "demo_personas.md").read_text(encoding="utf-8")
    for p in demo.PERSONAS:
        assert f"`{p.username}`" in sheet and passwords[p.username] in sheet
    assert "Try:" in sheet and "Pipeline Test" in sheet and "Never enrolled" in sheet
    assert f"`student_A` = {A}" in sheet and "ME1001 Engineering Mechanics" in sheet


def test_remove_deletes_only_the_demo(env):
    auth.create_user("real_teacher", "teacher", "Real", "real-password")
    auth.create_user("real_student", "student", "Real S", "real-password", student_id="R001")
    real_course = courses.create_course("PH101", "Physics", "real_teacher")
    courses.enrol(real_course, "R001", "real_teacher")
    real = storage.create_exam("Real exam", owner="real_teacher", course_id=real_course)
    demo.seed(app_data=env)
    demo.remove(app_data=env)
    assert sorted(u["username"] for u in auth.list_users()) == ["real_student", "real_teacher"]
    assert [e["id"] for e in storage.list_exams()] == [real]
    assert [c["code"] for c in courses.list_courses()] == ["PH101"]
    assert [s["student_id"] for s in students.all_students()] == ["R001"]
    assert courses.is_enrolled(real_course, "R001")
    assert not regrades.list_requests(MECH) and not (env / "demo_personas.md").exists()


def page(username: str, role: str, student_id: str | None = None) -> AppTest:
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = {
        "username": username,
        "role": role,
        "name": "",
        "student_id": student_id,
    }
    at.run()
    assert not at.exception, (username, [e.value for e in at.exception])
    return at


def test_every_persona_page_renders(seeded):
    for p in demo.PERSONAS:
        assert page(p.username, p.role, p.student_id or None).markdown  # something was drawn
    teacher = page("teacher_1", "teacher")
    shown = " ".join(m.value for m in teacher.markdown)
    assert "Mechanics Quiz" in shown and "Pipeline Test" in shown and "Circuits Quiz" not in shown
    assert next(m for m in teacher.metric if m.label == "Regrade requests").value == "1"
    assert "Circuits Quiz" in " ".join(m.value for m in page("teacher_2", "teacher").markdown)
    a_card = " ".join(m.value for m in page("student_A", "student", A).markdown)
    assert "Teacher 1" in a_card and "Teacher 2" in a_card  # both professors on A's grade card
    d_card = " ".join(m.value for m in page("student_D", "student", D).markdown)
    assert "Teacher 2" in d_card and "Teacher 1" not in d_card
    g_page = page("student_G", "student", G)
    assert any("not enrolled in any course" in i.value for i in g_page.info)

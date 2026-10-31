"""Students, courses, enrolments and the grade card: the database relations and how they gate and
update what a student sees."""

from __future__ import annotations

import sqlite3

import pytest
from streamlit.testing.v1 import AppTest

from app import config
from app.services import (
    auth,
    courses,
    db,
    gradecard,
    grades,
    publishing,
    regrades,
    roster,
    storage,
    students,
)
from app_support import fabricate_run

MAIN = str(config.ROOT / "app" / "main.py")
REASON = "I wrote the correct value and the working shows it clearly."


@pytest.fixture
def world(env):
    """Two teachers, each with a course; S1 and S2 as people; one marked exam per course.

    exam_x belongs to t1's course and was marked for S1 and S2 (marks 3 and 5 of 5... see
    app_support); exam_y belongs to t2's course. Nobody is enrolled yet."""
    auth.create_user("t1", "teacher", "Teacher One", "teacher-pass")
    auth.create_user("t2", "teacher", "Teacher Two", "teacher-pass")
    c1 = courses.create_course("ME1", "Mechanics", "t1", "2026")
    c2 = courses.create_course("EE1", "Circuits", "t2", "2026")
    x = storage.create_exam("Exam X", owner="t1", course_id=c1)
    y = storage.create_exam("Exam Y", owner="t2", course_id=c2)
    for eid in (x, y):
        storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
        storage.save_uploads(eid, "answers", [("a.md", b"a")], False, set())
        fabricate_run(eid)
    return {"c1": c1, "c2": c2, "x": x, "y": y}


def make_student(sid: str, username: str | None = None) -> None:
    auth.create_user(username or sid, "student", sid, "student-pass", student_id=sid)


# ---------- identity ----------


def test_a_student_id_is_unique_and_separate_from_the_username(env):
    auth.create_user("student_A", "student", "Asha", "student-pass", student_id="S24001")
    user = auth.authenticate("student_A", "student-pass")
    assert user["student_id"] == "S24001" and user["username"] == "student_A"
    assert students.account_of("S24001") == "student_A"
    with pytest.raises(ValueError, match="already has an account"):
        auth.create_user("someone_else", "student", "X", "student-pass", student_id="S24001")
    assert students.get(" S24001 ")["name"] == "Asha"  # ids are cleaned before lookup


def test_a_student_id_defaults_to_the_username(env):
    auth.create_user("S77", "student", "Zed", "student-pass")
    assert auth.authenticate("S77", "student-pass")["student_id"] == "S77"


def test_an_old_database_is_upgraded_in_place(env):
    """A database from before students had their own ids: the account keeps working."""
    with sqlite3.connect(db.PATH) as old:
        old.executescript(
            "CREATE TABLE users (username TEXT PRIMARY KEY, role TEXT NOT NULL, "
            "name TEXT NOT NULL DEFAULT '', pw_hash TEXT NOT NULL, "
            "active INTEGER NOT NULL DEFAULT 1, created TEXT NOT NULL);"
        )
        old.execute(
            "INSERT INTO users VALUES ('legacy_student', 'student', 'Leg', ?, 1, 'then')",
            (auth.hash_password("old-password"),),
        )
    user = auth.authenticate("legacy_student", "old-password")
    assert user["student_id"] == "legacy_student"  # linked to a student of the same id
    assert students.get("legacy_student")["name"] == "Leg"


# ---------- courses and enrolment ----------


def test_the_same_code_can_run_under_two_teachers_but_not_twice_under_one(world):
    other = courses.create_course("ME1", "Mechanics", "t2", "2026")  # same code, other teacher
    assert other != world["c1"]
    with pytest.raises(ValueError, match="already has a course ME1"):
        courses.create_course("ME1", "Again", "t1", "2026")
    assert [c["teacher"] for c in courses.list_courses() if c["code"] == "ME1"] == ["t1", "t2"]
    assert [c["code"] for c in courses.list_courses("t2")] == ["EE1", "ME1"]


def test_enrol_drop_and_re_enrol(world):
    make_student("S1")
    c = world["c1"]
    courses.enrol(c, "S1", "t1")
    assert courses.is_enrolled(c, "S1") and [r["student_id"] for r in courses.roster(c)] == ["S1"]
    courses.drop(c, "S1", "t1")
    assert not courses.is_enrolled(c, "S1") and courses.roster(c) == []
    assert courses.roster(c, include_dropped=True)[0]["status"] == "dropped"
    courses.enrol(c, "S1", "t1")  # coming back
    assert courses.is_enrolled(c, "S1") and len(courses.roster(c, include_dropped=True)) == 1


def test_one_student_in_many_courses_under_many_teachers(world):
    make_student("S1")
    courses.enrol(world["c1"], "S1", "t1")
    courses.enrol(world["c2"], "S1", "t2")
    assert [c["teacher"] for c in courses.courses_of("S1")] == ["t2", "t1"]  # EE1 sorts first
    courses.drop(world["c1"], "S1", "t1")
    assert [c["code"] for c in courses.courses_of("S1")] == ["EE1"]
    assert {c["code"] for c in courses.courses_of("S1", include_dropped=True)} == {"EE1", "ME1"}


def test_a_course_with_exams_cannot_be_deleted(world):
    with pytest.raises(ValueError, match="still has exams"):
        courses.delete_course(world["c1"], "t1")
    storage.delete_exam(world["x"])
    courses.delete_course(world["c1"], "t1")
    assert courses.get(world["c1"]) is None


# ---------- who may see an exam ----------


def test_publication_marks_and_enrolment_are_all_needed(world):
    x, c = world["x"], world["c1"]
    make_student("S1")
    publishing.publish(x, "t1")
    assert not publishing.can_view(x, "S1")  # published and marked, but not enrolled
    courses.enrol(c, "S1", "t1")
    assert publishing.can_view(x, "S1")
    make_student("S9")
    courses.enrol(c, "S9", "t1")
    assert not publishing.can_view(x, "S9")  # enrolled and published, but has no marks in it
    courses.drop(c, "S1", "t1")
    assert not publishing.can_view(x, "S1")
    with pytest.raises(PermissionError):
        publishing.student_view(x, "S1")


def test_a_dropped_student_cannot_file_a_regrade(world):
    x, c = world["x"], world["c1"]
    make_student("S1")
    courses.enrol(c, "S1", "t1")
    publishing.publish(x, "t1")
    courses.drop(c, "S1", "t1")
    with pytest.raises(PermissionError):
        regrades.submit(x, "S1", "1", "misread", REASON)


def test_roster_problems_name_who_is_marked_but_not_enrolled_and_who_is_absent(world):
    x, c = world["x"], world["c1"]
    for sid in ("S1", "S3"):
        make_student(sid)
    courses.enrol(c, "S1", "t1")  # S1 marked and enrolled
    courses.enrol(c, "S3", "t1")  # S3 enrolled but not marked; S2 marked but not enrolled
    assert publishing.roster_problems(x) == {"not_enrolled": ["S2"], "no_marks": ["S3"]}
    assert publishing.roster_problems(world["y"]) == {"not_enrolled": ["S1", "S2"], "no_marks": []}


# ---------- the grade card ----------


def test_enrolled_under_one_teacher_the_other_teacher_does_not_appear(world):
    make_student("S1")
    courses.enrol(world["c1"], "S1", "t1")
    publishing.publish(world["x"], "t1")
    publishing.publish(world["y"], "t2")
    card = gradecard.for_student("S1")
    assert [c["course"]["code"] for c in card["courses"]] == ["ME1"]
    assert card["courses"][0]["exams"][0]["title"] == "Exam X"


def test_enrolled_under_both_teachers_the_card_shows_both_and_averages_them(world):
    make_student("S1")
    courses.enrol(world["c1"], "S1", "t1")
    courses.enrol(world["c2"], "S1", "t2")
    publishing.publish(world["x"], "t1")
    publishing.publish(world["y"], "t2")
    card = gradecard.for_student("S1")
    assert {c["course"]["teacher"] for c in card["courses"]} == {"t1", "t2"}
    assert [c["percent"] for c in card["courses"]] == [60.0, 60.0]  # S1 has 3 of 5 in each
    assert card["overall_percent"] == 60.0


def test_an_unpublished_exam_is_not_on_the_card_and_a_course_without_results_has_no_percent(world):
    make_student("S1")
    courses.enrol(world["c1"], "S1", "t1")
    card = gradecard.for_student("S1")
    assert card["courses"][0]["exams"] == [] and card["courses"][0]["percent"] is None
    assert card["overall_percent"] is None


def course_percents(student_id: str) -> dict[str, float | None]:
    return {c["course"]["code"]: c["percent"] for c in gradecard.for_student(student_id)["courses"]}


def test_the_card_follows_an_override_a_regrade_a_publish_and_a_drop(world):
    make_student("S1")
    courses.enrol(world["c1"], "S1", "t1")
    courses.enrol(world["c2"], "S1", "t2")
    publishing.publish(world["x"], "t1")
    assert course_percents("S1") == {"ME1": 60.0, "EE1": None}  # EE1 not published yet
    publishing.publish(world["y"], "t2")
    assert course_percents("S1") == {"ME1": 60.0, "EE1": 60.0}
    grades.override(
        world["y"], "S1", "1", 2.0, "Method was fine.", by="t2"
    )  # teacher 2 raises a mark
    assert course_percents("S1") == {"ME1": 60.0, "EE1": 80.0}  # only teacher 2's course moved
    rid = regrades.submit(world["x"], "S1", "2", "misread", REASON)
    regrades.decide(rid, upheld=True, reply="Agreed.", by="t1", new_mark=3.0)  # teacher 1 upholds
    assert course_percents("S1") == {"ME1": 80.0, "EE1": 80.0}
    courses.drop(world["c2"], "S1", "t2")
    assert course_percents("S1") == {"ME1": 80.0}
    assert gradecard.for_student("S1")["overall_percent"] == 80.0
    courses.enrol(world["c2"], "S1", "t2")  # re-enrolled: it comes straight back
    assert course_percents("S1") == {"ME1": 80.0, "EE1": 80.0}


def test_a_card_never_shows_another_students_marks(world):
    for sid in ("S1", "S2"):
        make_student(sid)
        courses.enrol(world["c1"], sid, "t1")
    publishing.publish(world["x"], "t1")
    s1, s2 = gradecard.for_student("S1"), gradecard.for_student("S2")
    assert s1["courses"][0]["total"] == 3.0 and s2["courses"][0]["total"] == 5.0


# ---------- rosters ----------


def test_enrol_csv_enrols_the_class_and_creates_missing_accounts(world):
    make_student("S1")  # already has an account
    data = b"student_id,name,email\nS1,Asha,a@x\nS5,Ben,b@x\nS6,Cy,c@x\n"
    rows = roster.enrol_csv(world["c1"], data, by="t1")
    assert {r["student"]: r["status"] for r in rows} == {
        "S1": "exists",
        "S5": "created",
        "S6": "created",
    }
    assert [r["student_id"] for r in courses.roster(world["c1"])] == ["S1", "S5", "S6"]
    assert students.get("S5")["email"] == "b@x"
    assert auth.authenticate("S5", next(r["password"] for r in rows if r["student"] == "S5"))
    assert roster.enrol_csv(world["c1"], data, by="t1")[1]["status"] == "exists"  # idempotent


def test_exam_roster_enrols_into_the_exams_course_and_flags_a_taken_username(world):
    auth.create_user("S2", "teacher", "A teacher using S2 as a username", "teacher-pass")
    make_student("S1", username="login_one")  # username differs from the student id
    rows = {r["student"]: r for r in roster.create_accounts(world["x"], by="t1")}
    assert rows["S1"]["status"] == "exists" and rows["S1"]["username"] == "login_one"
    assert rows["S2"]["status"] == "conflict" and rows["S2"]["password"] == ""
    assert {r["student_id"] for r in courses.roster(world["c1"])} == {
        "S1",
        "S2",
    }  # both enrolled anyway


# ---------- pages ----------


def sign_in(user: dict) -> AppTest:
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = user
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_the_student_page_shows_the_grade_card_for_the_signed_in_student_id(world):
    auth.create_user("student_A", "student", "Asha", "student-pass", student_id="S1")
    courses.enrol(world["c1"], "S1", "t1")
    courses.enrol(world["c2"], "S1", "t2")
    publishing.publish(world["x"], "t1")
    publishing.publish(world["y"], "t2")
    me = auth.authenticate("student_A", "student-pass")
    at = sign_in(me)
    shown = " ".join(m.value for m in at.markdown)
    assert "ME1 · Mechanics" in shown and "EE1 · Circuits" in shown and "student id S1" in shown
    assert "Teacher One" in shown and "Teacher Two" in shown


def test_a_student_enrolled_nowhere_sees_an_empty_card(world):
    make_student("S1")
    at = sign_in(auth.authenticate("S1", "student-pass"))
    assert any("not enrolled in any course" in i.value for i in at.info)


def test_the_teacher_courses_tab_and_the_admin_people_tab_render(world):
    make_student("S1")
    courses.enrol(world["c1"], "S1", "t1")
    teacher = sign_in(auth.authenticate("t1", "teacher-pass"))
    assert "ME1 · Mechanics" in " ".join(e.label for e in teacher.expander)
    auth.create_user("boss", "admin", "B", "long-password")
    admin = sign_in(auth.authenticate("boss", "long-password"))
    assert "Courses" in [h.value for h in admin.subheader] and "Students" in [
        h.value for h in admin.subheader
    ]

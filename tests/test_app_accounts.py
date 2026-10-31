"""Accounts, mark overrides, the publish gate, student isolation and regrade limits."""

from __future__ import annotations

from datetime import date, timedelta

import pytest
from streamlit.testing.v1 import AppTest

from app import config
from app.services import auth, grades, publishing, regrades, report, roster, storage
from app_support import fabricate_run

MAIN = str(config.ROOT / "app" / "main.py")
REASON = "I wrote the correct value and the working shows it clearly."


@pytest.fixture
def exam(env):
    """A marked exam owned by teacher t1 with accounts for S1 and S2, not yet published."""
    auth.create_user("t1", "teacher", "Teacher", "teacher-pass")
    eid = storage.create_exam("Quiz", owner="t1")
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(eid, "answers", [("a.md", b"a")], False, set())
    fabricate_run(eid)
    for s in ("S1", "S2"):
        auth.create_user(s, "student", "", "student-pass")
    return eid


# ---------- accounts ----------


def test_passwords_are_hashed_and_checked(env):
    auth.create_user("t1", "teacher", "T", "teacher-pass")
    assert auth.authenticate("t1", "teacher-pass")["role"] == "teacher"
    assert auth.authenticate("t1", "wrong") is None
    assert auth.authenticate("nobody", "teacher-pass") is None
    with auth.db.connect() as c:
        stored = c.execute("SELECT pw_hash FROM users").fetchone()[0]
    assert "teacher-pass" not in stored and stored.startswith("scrypt$")


def test_disabled_user_cannot_sign_in_and_rules_are_enforced(env):
    auth.create_user("t1", "teacher", "T", "teacher-pass")
    auth.set_active("t1", False, by="admin")
    assert auth.authenticate("t1", "teacher-pass") is None
    with pytest.raises(ValueError, match="taken"):
        auth.create_user("t1", "teacher", "T", "teacher-pass")
    with pytest.raises(ValueError, match="at least"):
        auth.create_user("x", "teacher", "T", "short")
    with pytest.raises(ValueError, match="role"):
        auth.create_user("x", "root", "T", "long-enough-pass")


def test_roster_creates_accounts_once_with_names(env):
    eid = storage.create_exam("Quiz", owner="t1")
    storage.save_uploads(eid, "paper", [("p.md", b"q")], False, set())
    storage.save_uploads(
        eid,
        "answers",
        [("a.md", b"a"), ("r.csv", b"Student_ID,Name\nS1,Asha\n")],
        False,
        {".csv"},
    )
    fabricate_run(eid)
    first = roster.create_accounts(eid, by="t1")
    assert {r["student"]: r["status"] for r in first} == {"S1": "created", "S2": "created"}
    assert all(len(r["password"]) >= auth.MIN_PASSWORD for r in first)
    assert next(r for r in first if r["student"] == "S1")["name"] == "Asha"
    assert auth.authenticate("S1", first[0]["password"])
    again = roster.create_accounts(eid, by="t1")
    assert {r["status"] for r in again} == {"exists"} and not any(r["password"] for r in again)


def test_roster_needs_an_id_column():
    with pytest.raises(ValueError, match="student_id"):
        roster.parse_roster(b"name,email\nAsha,a@x\n")


# ---------- overrides ----------


def test_override_changes_marks_totals_and_exports(exam):
    assert grades.marks_table(exam).set_index("student").loc["S1", "total"] == 3.0
    grades.override(exam, "S1", "1", 2.0, "Method was fine.", by="t1")
    assert grades.marks_table(exam).set_index("student").loc["S1", "total"] == 4.0
    assert grades.final_marks(exam)["S1"]["1"] == 2.0
    row = next(r for r in report.rows(exam, "S1") if r["question"] == "1")
    assert row["overridden"] and row["model_mark"] == 1.0 and row["mark"] == 2.0
    assert "changed by the teacher (was 1)" in report.markdown(exam, "S1")
    grades.clear_override(exam, "S1", "1", by="t1")
    assert grades.final_marks(exam)["S1"]["1"] == 1.0


def test_override_must_stay_within_the_question(exam):
    with pytest.raises(ValueError, match="between 0 and 2"):
        grades.override(exam, "S1", "1", 2.5, "", by="t1")
    with pytest.raises(ValueError, match="No question"):
        grades.override(exam, "S1", "9", 1, "", by="t1")


def test_best_of_n_applies_to_totals(exam):
    storage.update_settings(exam, count_best=1)
    table = grades.marks_table(exam).set_index("student")
    assert table.loc["S1", "counted_total"] == 2.0  # best single question: 2 of 3
    assert table.loc["S2", "counted_total"] == 3.0


# ---------- the publish gate ----------


def test_students_see_nothing_until_published(exam):
    assert publishing.exams_for_student("S1") == []
    with pytest.raises(PermissionError):
        publishing.student_view(exam, "S1")
    publishing.publish(exam, by="t1")
    assert [m["id"] for m in publishing.exams_for_student("S1")] == [exam]
    publishing.unpublish(exam, by="t1")
    with pytest.raises(PermissionError):
        publishing.student_view(exam, "S1")


def test_a_student_sees_only_their_own_rows(exam):
    publishing.publish(exam, by="t1")
    view = publishing.student_view(exam, "S1")
    text = str(view)
    assert "SECRET-S2" not in text and "note for S2" not in text
    assert view["total"] == 3.0 and view["out_of"] == 5.0
    with pytest.raises(PermissionError):  # someone who is not in the exam
        publishing.student_view(exam, "S3")


def test_policy_hides_the_reference_and_can_hide_the_answer(exam):
    publishing.publish(exam, by="t1")
    rows = publishing.student_view(exam, "S1")["rows"]
    assert all(r["reference"] == "" and r["answer"] for r in rows)
    storage.update_policy(exam, show_reference=True, show_answer=False)
    rows = publishing.student_view(exam, "S1")["rows"]
    assert all(r["reference"] == "MODEL-ANSWER" and r["answer"] == "" for r in rows)
    assert not any(
        "model_mark" in r or "flags" in r for r in rows
    )  # internals never reach students


def test_cannot_publish_before_marking(env):
    eid = storage.create_exam("Quiz", owner="t1")
    with pytest.raises(ValueError, match="Mark the exam"):
        publishing.publish(eid, by="t1")


def test_cannot_unpublish_after_a_regrade_request(exam):
    publishing.publish(exam, by="t1")
    regrades.submit(exam, "S1", "1", "misread", REASON)
    with pytest.raises(ValueError, match="no longer be undone"):
        publishing.unpublish(exam, by="t1")


# ---------- regrades ----------


def test_regrade_needs_publication_and_a_real_reason(exam):
    with pytest.raises(PermissionError):
        regrades.submit(exam, "S1", "1", "misread", REASON)
    publishing.publish(exam, by="t1")
    with pytest.raises(ValueError, match="at least 40"):
        regrades.submit(exam, "S1", "1", "misread", "unfair")
    with pytest.raises(ValueError, match="Choose what"):
        regrades.submit(exam, "S1", "1", "nonsense", REASON)
    with pytest.raises(ValueError, match="not marked"):
        regrades.submit(exam, "S1", "7", "misread", REASON)


def test_limits_per_question_and_in_total(exam):
    publishing.publish(exam, by="t1")
    storage.update_policy(exam, regrade_max_total=2, regrade_max_per_question=1)
    regrades.submit(exam, "S1", "1", "misread", REASON)
    with pytest.raises(ValueError, match="most times"):
        regrades.submit(exam, "S1", "1", "misread", REASON)
    regrades.submit(exam, "S1", "2", "missed_point", REASON)
    assert regrades.allowance(exam, "S1")["left"] == 0
    with pytest.raises(ValueError, match="used all 2"):
        regrades.submit(exam, "S1", "2", "missed_point", REASON)
    assert regrades.allowance(exam, "S2")["left"] == 2  # S2's allowance is separate


def test_a_rejected_request_uses_an_attempt_unless_refunded(exam):
    publishing.publish(exam, by="t1")
    storage.update_policy(exam, regrade_max_total=1, regrade_max_per_question=2)
    rid = regrades.submit(exam, "S1", "1", "misread", REASON)
    regrades.decide(rid, upheld=False, reply="The answer is incomplete.", by="t1")
    assert regrades.allowance(exam, "S1")["left"] == 0
    storage.update_policy(exam, rejected_refunds=True)
    assert regrades.allowance(exam, "S1")["left"] == 1


def test_deadline_and_switch_close_requests(exam):
    publishing.publish(exam, by="t1")
    storage.update_policy(exam, regrade_deadline=(date.today() - timedelta(days=1)).isoformat())
    with pytest.raises(ValueError, match="deadline"):
        regrades.submit(exam, "S1", "1", "misread", REASON)
    storage.update_policy(exam, regrade_deadline="", regrade_enabled=False)
    with pytest.raises(ValueError, match="not open"):
        regrades.submit(exam, "S1", "1", "misread", REASON)


def test_upholding_changes_the_mark_and_rejecting_keeps_it(exam):
    publishing.publish(exam, by="t1")
    storage.update_policy(exam, regrade_max_per_question=2)
    up = regrades.submit(exam, "S1", "1", "missed_point", REASON)
    regrades.decide(up, upheld=True, reply="You are right.", by="t1", new_mark=2.0)
    assert publishing.student_view(exam, "S1")["total"] == 4.0
    mine = regrades.list_requests(exam, "S1")[0]
    assert (mine["status"], mine["old_mark"], mine["new_mark"]) == ("upheld", 1.0, 2.0)
    down = regrades.submit(exam, "S1", "1", "other", REASON + " Please look again.")
    regrades.decide(down, upheld=False, reply="Mark stands.", by="t1")
    assert publishing.student_view(exam, "S1")["total"] == 4.0
    with pytest.raises(ValueError, match="not waiting"):
        regrades.decide(down, upheld=False, reply="again", by="t1")


def test_decisions_need_a_reply_and_a_mark(exam):
    publishing.publish(exam, by="t1")
    rid = regrades.submit(exam, "S1", "1", "misread", REASON)
    with pytest.raises(ValueError, match="reply"):
        regrades.decide(rid, upheld=False, reply=" ", by="t1")
    with pytest.raises(ValueError, match="new mark"):
        regrades.decide(rid, upheld=True, reply="ok", by="t1")
    with pytest.raises(ValueError, match="between 0 and 2"):
        regrades.decide(rid, upheld=True, reply="ok", by="t1", new_mark=9)
    assert regrades.list_requests(exam, status="pending")  # still waiting after the failures


# ---------- pages ----------


def page(user: dict, **state) -> AppTest:
    at = AppTest.from_file(MAIN, default_timeout=60)
    at.session_state["user"] = user
    for k, v in state.items():
        at.session_state[k] = v
    at.run()
    assert not at.exception, [e.value for e in at.exception]
    return at


def test_student_page_before_and_after_publishing(exam):
    s1 = {"username": "S1", "role": "student", "name": ""}
    at = page(s1)
    assert any("No results have been published" in i.value for i in at.info)
    publishing.publish(exam, by="t1")
    at = page(s1)
    shown = " ".join(m.value for m in at.markdown)
    assert "/ 5 · 60%" in shown and "SECRET-S2" not in shown
    assert "Ask for a regrade" in [h.value for h in at.subheader]


def test_student_submits_a_regrade_through_the_form(exam):
    publishing.publish(exam, by="t1")
    at = page({"username": "S1", "role": "student", "name": ""})
    at.text_area[0].set_value(REASON)
    at.button[0].click().run()
    assert not at.exception, [e.value for e in at.exception]
    assert len(regrades.list_requests(exam, "S1")) == 1


def test_teacher_sees_only_own_exams_and_the_inbox(exam):
    auth.create_user("t2", "teacher", "T2", "teacher-pass")
    other = storage.create_exam("Theirs", owner="t2")
    publishing.publish(exam, by="t1")
    regrades.submit(exam, "S1", "1", "misread", REASON)
    at = page({"username": "t1", "role": "teacher", "name": ""})
    shown = " ".join(m.value for m in at.markdown)
    assert "Quiz" in shown and "Theirs" not in shown  # only own exams, on the overview
    assert next(m for m in at.metric if m.label == "Regrade requests").value == "1"
    at.button(key=f"open_{exam}").click().run()
    assert not at.exception and "Waiting for you (1)" in [h.value for h in at.subheader]
    at2 = page({"username": "t2", "role": "teacher", "name": ""}, exam_id=exam)  # not theirs
    assert "Theirs" in " ".join(m.value for m in at2.markdown) and other
    assert "exam_id" not in at2.session_state  # someone else's exam is never opened

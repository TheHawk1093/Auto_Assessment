"""Teacher home, Courses tab: the courses a teacher runs and who is enrolled in each.

A course is one offering by one teacher. Enrol a class from a roster CSV or one student at a time;
a student can be in several courses, under this teacher, another, or both.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services import courses, roster, storage, students
from app.ui import session


def render() -> None:
    """Show the teacher's courses with their enrolments."""
    user = session.current_user()
    mine = courses.list_courses(None if user["role"] == "admin" else user["username"])
    _new_course(user)
    if not mine:
        st.info("No courses yet. Create one above, then enrol students and attach exams to it.")
        return
    for course in mine:
        _course(course, user["username"])


def _new_course(user: dict) -> None:
    with st.expander("＋ New course"), st.form("new_course", clear_on_submit=True, border=False):
        c1, c2, c3 = st.columns([1, 2, 1])
        code = c1.text_input("Code", placeholder="ME1001")
        title = c2.text_input("Title", placeholder="Engineering Mechanics")
        term = c3.text_input("Term", placeholder="2026 Autumn")
        if st.form_submit_button("Create course", type="primary"):
            try:
                courses.create_course(code, title, user["username"], term)
            except ValueError as e:
                st.error(str(e))
            else:
                st.rerun()


def _course(course: dict, me: str) -> None:
    people = courses.roster(course["id"], include_dropped=True)
    active = [p for p in people if p["status"] == "active"]
    exams = [m for m in storage.list_exams() if m["course_id"] == course["id"]]
    who = course["teacher_name"] or course["teacher"]
    title = (
        f"{course['code']} · {course['title']} — {who} ({len(active)} enrolled, {len(exams)} exams)"
    )
    with st.expander(title):
        _edit_course(course, me)
        if people:
            _roster_editor(course["id"], people, me)
        else:
            st.caption("Nobody is enrolled yet.")
        _enrol_forms(course, active, me)
        if not exams and st.button("Delete this course", key=f"delcourse_{course['id']}"):
            courses.delete_course(course["id"], me)
            st.rerun()


def _enrol_forms(course: dict, active: list[dict], me: str) -> None:
    cid = course["id"]
    left, right = st.columns(2)
    with left:
        upload = st.file_uploader(
            "Enrol a class from a roster CSV (student_id, name, email)",
            type=["csv"],
            key=f"roster_{cid}",
        )
        if upload and st.button(
            "Enrol the class and create missing accounts", key=f"enrolcsv_{cid}"
        ):
            try:
                rows = roster.enrol_csv(cid, upload.getvalue(), me)
            except ValueError as e:
                st.error(str(e))
            else:
                st.session_state[f"issued_{cid}"] = [r for r in rows if r["status"] == "created"]
                st.success(f"Enrolled {len(rows)} students.")
    with right:
        with st.form(f"add_{cid}", clear_on_submit=True, border=False):
            sid = st.text_input("Add one student (student id)", key=f"addid_{cid}")
            name = st.text_input("Name (optional)", key=f"addname_{cid}")
            if st.form_submit_button("Enrol"):
                try:
                    courses.enrol(cid, sid, me, name)
                except ValueError as e:
                    st.error(str(e))
                else:
                    st.rerun()
        if active:
            drop = st.selectbox(
                "Remove a student", [p["student_id"] for p in active], key=f"dropid_{cid}"
            )
            if st.button("Remove from course", key=f"drop_{cid}"):
                courses.drop(cid, drop, me)
                st.rerun()
    issued = st.session_state.get(f"issued_{cid}")
    if issued:
        st.warning("First passwords for new accounts are shown only now.")
        table = pd.DataFrame(issued)[["student", "name", "username", "password"]]
        st.dataframe(table, hide_index=True, width="stretch")


def _edit_course(course: dict, me: str) -> None:
    """Rename a course or change its term. The code stays: exams and records refer to it."""
    with st.form(f"edit_course_{course['id']}", border=False):
        c1, c2, c3, c4 = st.columns([1, 2, 1, 1], vertical_alignment="bottom")
        c1.text_input("Code (fixed)", course["code"], disabled=True)
        title = c2.text_input("Title", course["title"])
        term = c3.text_input("Term", course["term"])
        if c4.form_submit_button("Save course"):
            try:
                courses.update_course(course["id"], title, term, me)
            except ValueError as e:
                st.error(str(e))
            else:
                st.rerun()


def _roster_editor(course_id: int, people: list[dict], me: str) -> None:
    """The roster, with names and emails editable. The roll number and account are fixed."""
    table = pd.DataFrame(people)[["student_id", "name", "email", "username", "status"]]
    edited = st.data_editor(
        table, hide_index=True, width="stretch", key=f"roster_edit_{course_id}",
        disabled=["student_id", "username", "status"],
    )  # fmt: skip
    changed = [
        (old.student_id, new["name"], new["email"])
        for old, (_, new) in zip(table.itertuples(), edited.iterrows(), strict=True)
        if (old.name, old.email) != (new["name"], new["email"])
    ]
    st.caption(
        "Roll numbers and usernames are fixed. A name or email you change here changes it for the "
        "student everywhere, including other teachers' courses."
    )
    if changed and st.button(
        f"Save {len(changed)} change(s) to students", key=f"roster_save_{course_id}"
    ):
        for sid, name, email in changed:
            students.update(sid, name or "", email or "", me)
        st.rerun()

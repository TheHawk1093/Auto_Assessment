"""Tab 5: who sees what. Student accounts, the rules for students, and the publish switch."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from app.services import courses, publishing, results, roster, storage
from app.ui import session


def render(exam_id: str) -> None:
    """Show enrolment, student rules and the publish switch for a marked exam."""
    if not results.has_results(exam_id):
        st.info("Publishing is available once marking has finished (step 3).")
        return
    meta = storage.load_meta(exam_id)
    _accounts(exam_id)
    _policy(exam_id, meta["policy"])
    _switch(exam_id, meta)


def _accounts(exam_id: str) -> None:
    st.subheader("Enrolment and accounts")
    meta = storage.load_meta(exam_id)
    course = courses.get(meta["course_id"])
    students = results.intake(exam_id).get("students", [])
    if course is None:
        st.warning(
            "This exam is not in a course, so enrolment is not checked: anyone marked in it can "
            "see their results once published. Put it in a course (Courses tab on the home page)."
        )
    else:
        st.caption(
            f"{len(students)} students found in the answers. Students are enrolled in "
            f"**{courses.label(course)}**; a student sees this exam only while enrolled there, "
            "and only after you publish."
        )
    if roster.roster_file(exam_id):
        st.caption(f"Names and emails are read from {roster.roster_file(exam_id).name}.")
    _problems(exam_id)
    key = f"new_accounts_{exam_id}"
    if st.button("Enrol students and create missing accounts"):
        try:
            st.session_state[key] = roster.create_accounts(
                exam_id, session.current_user()["username"]
            )
        except ValueError as e:
            st.error(str(e))
        else:
            st.rerun()
    done = st.session_state.get(key, [])
    made = [r for r in done if r["status"] == "created"]
    if done:
        clash = [r["student"] for r in done if r["status"] == "conflict"]
        st.success(
            f"{len(made)} account(s) created, {len(done) - len(made) - len(clash)} already existed."
        )
        if clash:
            st.error(
                f"No account made for {', '.join(clash)}: that username is taken by someone else."
            )
    if made:
        st.warning("These first passwords are shown only now. Download them and hand them out.")
        table = pd.DataFrame(made)[["student", "name", "username", "password"]]
        st.dataframe(table, hide_index=True, width="stretch")
        csv = table.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download passwords (CSV)", csv, "student_passwords.csv", "text/csv")


def _problems(exam_id: str) -> None:
    """Who was marked but cannot see the results, and who is enrolled but was not marked."""
    problems = publishing.roster_problems(exam_id)
    if problems["not_enrolled"]:
        st.warning(
            "Marked but not enrolled in this course, so they cannot see their results: "
            + ", ".join(problems["not_enrolled"])
            + ". Press the button below to enrol them."
        )
    if problems["no_marks"]:
        st.info(
            "Enrolled but no answers were marked (absent, or the file name did not match the "
            "student id): " + ", ".join(problems["no_marks"])
        )


def _policy(exam_id: str, p: dict) -> None:
    st.subheader("What students can do")
    with st.form("policy"):
        c1, c2 = st.columns(2)
        show_answer = c1.checkbox("Show students their own answer", value=p["show_answer"])
        show_ref = c2.checkbox("Show students the model answer", value=p["show_reference"])
        enabled = st.checkbox("Allow regrade requests", value=p["regrade_enabled"])
        c3, c4, c5 = st.columns(3)
        total = c3.number_input("Requests per student", 0, 20, int(p["regrade_max_total"]))
        per_q = c4.number_input("Requests per question", 1, 10, int(p["regrade_max_per_question"]))
        min_chars = c5.number_input(
            "Shortest reason (characters)", 0, 500, int(p["regrade_min_chars"])
        )
        c6, c7 = st.columns(2)
        use_deadline = c6.checkbox("Set a deadline", value=bool(p["regrade_deadline"]))
        deadline = c7.date_input(
            "Last day to ask",
            value=date.fromisoformat(p["regrade_deadline"])
            if p["regrade_deadline"]
            else date.today(),
        )
        refund = st.checkbox(
            "A rejected request does not use up an attempt", value=p["rejected_refunds"]
        )
        if st.form_submit_button("Save", type="primary"):
            storage.update_policy(
                exam_id,
                show_answer=show_answer,
                show_reference=show_ref,
                regrade_enabled=enabled,
                regrade_max_total=int(total),
                regrade_max_per_question=int(per_q),
                regrade_min_chars=int(min_chars),
                regrade_deadline=deadline.isoformat() if use_deadline else "",
                rejected_refunds=refund,
            )
            st.success("Saved.")


def _switch(exam_id: str, meta: dict) -> None:
    st.subheader("Publish")
    user = session.current_user()["username"]
    if meta["published"]:
        st.success(f"Published on {meta['published']}. Students can see their results.")
        if st.button("Unpublish"):
            try:
                publishing.unpublish(exam_id, user)
            except ValueError as e:
                st.error(str(e))
            else:
                st.rerun()
        return
    st.caption(
        "Review the marks first; later changes still reach students. Publishing makes every "
        "student's results and feedback visible to that student."
    )
    sure = st.checkbox(
        "I have checked the marks and want students to see them", key=f"sure_pub_{exam_id}"
    )
    if st.button("Publish to students", type="primary", disabled=not sure):
        publishing.publish(exam_id, user)
        st.rerun()

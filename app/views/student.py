"""Student page: grade card, exam details and regrade requests.

Shows the grade card across every course, one exam's marks and feedback, and regrade requests
within the teacher's limits. Everything is looked up by the student's unique id.
"""

from __future__ import annotations

import streamlit as st

from app.services import gradecard, publishing, regrades, students, submissions
from app.ui import components as ui
from app.ui import rich, session

STATUS = {
    "pending": ("Waiting for the teacher", "amber"),
    "upheld": ("Mark changed", "green"),
    "rejected": ("Mark kept", "neutral"),
}


def render() -> None:
    """Show the signed-in student's results page."""
    sid = session.student_id()
    ui.page_header(
        "My results",
        f"{students.name_of(sid)} · student id {sid}",
    )
    todo = [m for m in submissions.open_for(sid) if submissions.window(m["id"])[0]]
    work = ":material/assignment: Assignments" + (f" ({len(todo)})" if todo else "")
    card_tab, exam_tab, work_tab = st.tabs(
        [":material/school: Grade card", ":material/fact_check: Exam details", work]
    )
    with card_tab:
        _grade_card(sid)
    with exam_tab:
        _exam_details(sid)
    with work_tab:
        _hand_in(sid)


# ---------- grade card ----------


def _grade_card(sid: str) -> None:
    card = gradecard.for_student(sid)
    if not card["courses"]:
        st.info("You are not enrolled in any course yet.")
        return
    if card["overall_percent"] is not None:
        ui.score_card(
            "Overall", card["overall_percent"], 100, "Average of your course percentages."
        )
    for course in card["courses"]:
        _course(course)


def _course(entry: dict) -> None:
    course = entry["course"]
    with st.container(border=True):
        head, score = st.columns([3, 1], vertical_alignment="center")
        with head:
            st.markdown(f"**{course['code']} · {course['title']}**")
            who = course["teacher_name"] or course["teacher"]
            term = f" · {course['term']}" if course["term"] else ""
            st.markdown(ui.chips((who, "violet")) + f"<span>{term}</span>", unsafe_allow_html=True)
        with score:
            if entry["percent"] is None:
                st.caption("No published results yet")
            else:
                st.metric(
                    "Course",
                    f"{entry['percent']:g}%",
                    f"{entry['total']:g} / {entry['out_of']:g}",
                    delta_color="off",
                )
        for exam in entry["exams"]:
            left, mid, right = st.columns([3, 2, 2], vertical_alignment="center")
            left.markdown(exam["title"])
            mid.markdown(
                f"{exam['total']:g} / {exam['out_of']:g}" + ui.bar(exam["percent"] / 100),
                unsafe_allow_html=True,
            )
            if exam["pending_regrades"]:
                right.markdown(
                    ui.chip(f"{exam['pending_regrades']} regrade request(s) pending", "amber"),
                    unsafe_allow_html=True,
                )


# ---------- one exam ----------


def _exam_details(sid: str) -> None:
    exams = publishing.exams_for_student(sid)
    if not exams:
        st.info("No results have been published for you yet. Check back later.")
        return
    titles = {e["id"]: e["title"] for e in exams}
    exam_id = st.selectbox("Exam", list(titles), format_func=titles.get)
    view = publishing.student_view(exam_id, sid)  # the only way in: checks publish and enrolment
    ui.score_card(
        view["exam"], view["total"], view["out_of"], f"Published {view['published'][:10]}"
    )
    requests = regrades.list_requests(exam_id, sid)
    st.subheader("Question by question")
    for row in view["rows"]:
        _question(row, [r for r in requests if r["question"] == row["question"]])
    _regrade_form(exam_id, sid, view)


def _question(row: dict, requests: list[dict]) -> None:
    share = row["mark"] / row["max"] if row["max"] else 0.0
    head = f"Question {row['question']} · {row['mark']:g} / {row['max']:g}"
    pending = any(r["status"] == "pending" for r in requests)
    with st.expander(head + ("  ·  ⏳" if pending else ""), expanded=share < 1):
        st.markdown(ui.bar(share), unsafe_allow_html=True)
        tags = []
        if row["mark_changed"]:
            tags.append(("Changed by your teacher", "green"))
        tags += [STATUS[r["status"]] for r in requests]
        if tags:
            st.markdown(ui.chips(*tags), unsafe_allow_html=True)
        st.caption("Question")
        rich.markdown(row["text"])
        if row["teacher_comment"]:
            st.info(f"Teacher's note: {row['teacher_comment']}")
        st.markdown("**Feedback**")
        rich.rich_text(row["feedback"], empty="Full marks. Nothing to improve.")
        if row["answer"]:
            st.caption("Your answer")
            rich.rich_text(row["answer"])
        if row["reference"]:
            st.caption("Model answer")
            rich.rich_text(row["reference"])
        for r in requests:
            if r["reply"]:
                st.caption(f"Reply to your request #{r['id']}: {r['reply']}")


def _regrade_form(exam_id: str, sid: str, view: dict) -> None:
    st.subheader("Ask for a regrade")
    allow = regrades.allowance(exam_id, sid)
    if allow["closed"]:
        st.info(allow["closed"])
        return
    st.markdown(
        ui.chips((f"{allow['left']} of {allow['max_total']} requests left", "blue")),
        unsafe_allow_html=True,
    )
    st.caption(
        "Explain what you think was missed or marked wrongly, in at least "
        f"{allow['min_chars']} characters. Your teacher decides."
    )
    if allow["left"] <= 0:
        return
    questions = [r["question"] for r in view["rows"]]
    with st.form("regrade", clear_on_submit=True):
        question = st.selectbox("Question", questions)
        kind = st.selectbox(
            "What went wrong?", list(regrades.KINDS), format_func=regrades.KINDS.get
        )
        reason = st.text_area("Your reason")
        if st.form_submit_button("Send request", type="primary"):
            try:
                regrades.submit(exam_id, sid, question, kind, reason)
            except ValueError as e:
                st.error(str(e))
            else:
                st.success("Sent. Your teacher will reply here.")
                st.rerun()


# ---------- assignments ----------


def _hand_in(sid: str) -> None:
    """Assignments open for work: upload documents or photos; replace them until the deadline."""
    exams = submissions.open_for(sid)
    if not exams:
        st.info("No assignments are open for you.")
        return
    for meta in exams:
        _hand_in_one(meta, sid)


def _hand_in_one(meta: dict, sid: str) -> None:
    exam_id = meta["id"]
    is_open, why = submissions.window(exam_id)
    mine = submissions.status_of(exam_id, sid)
    sub = meta["submissions"]
    with st.container(border=True):
        st.markdown(f"**{meta['title']}**")
        chips = [("Open", "green")] if is_open else [(why, "neutral")]
        if sub["deadline"] and is_open:
            chips.append((f"Submit by {sub['deadline']}", "amber"))
        if mine:
            chips.append((f"Submitted {mine['at'][:16].replace('T', ' ')}", "blue"))
        st.markdown(ui.chips(*chips), unsafe_allow_html=True)
        if sub["instructions"]:
            st.markdown(sub["instructions"])
        if mine:
            st.caption("Your submission: " + ", ".join(mine["files"]))
        if not is_open:
            return
        nonce_key = f"submit_nonce_{exam_id}"
        nonce = st.session_state.setdefault(nonce_key, 0)
        picked = st.file_uploader(
            "Documents (txt, md, docx, pdf) or photos of your pages (png, jpg, webp)",
            type=["txt", "md", "docx", "pdf", "png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True, key=f"submit_{exam_id}_{nonce}",
        )  # fmt: skip
        if mine:
            st.caption("Submitting again replaces your earlier submission.")
        if st.button("Submit" if not mine else "Replace my submission", key=f"submit_go_{exam_id}",
                     type="primary", disabled=not picked):  # fmt: skip
            try:
                submissions.submit(exam_id, sid, [(f.name, f.getvalue()) for f in picked])
            except (PermissionError, ValueError) as e:
                st.error(str(e))
            else:
                st.session_state[nonce_key] = nonce + 1
                st.rerun()

"""Teacher home: every exam as a card, what needs attention, and a way to start a new one."""

from __future__ import annotations

from html import escape

import streamlit as st

from app.services import courses, overview, storage
from app.ui import components as ui
from app.ui import session
from app.views.teacher import courses as courses_tab

STATUS = {
    "draft": ("Needs files", "neutral"),
    "ready": ("Ready to prepare", "amber"),
    "prepared": ("Schemes written", "amber"),
    "marked": ("Marked", "green"),
    "published": ("Published", "blue"),
}
PER_ROW = 3


def render() -> None:
    """Show the exam cards, the new-exam button and the Courses tab."""
    user = session.current_user()
    head, a1, a2 = st.columns([4, 1, 1], vertical_alignment="bottom")
    with head:
        ui.page_header("Your work", "Exams and assignments: upload, mark, review and publish.")
    with a1:
        _new_exam(user, "exam")
    with a2:
        _new_exam(user, "assignment")
    exams_tab, work_tab, courses_view = st.tabs(
        [
            ":material/description: Exams",
            ":material/assignment: Assignments",
            ":material/groups: Courses",
        ]
    )
    with exams_tab:
        _exams(user, "exam")
    with work_tab:
        _exams(user, "assignment")
    with courses_view:
        courses_tab.render()


def _exams(user: dict, kind: str) -> None:
    cards = [
        c
        for c in overview.for_owner(None if user["role"] == "admin" else user["username"])
        if c["kind"] == kind
    ]
    if not cards:
        st.info(f"No {kind}s yet. Use “New {kind}” to create the first one.")
        return
    _attention(cards)
    for start in range(0, len(cards), PER_ROW):
        row = st.columns(PER_ROW)
        for col, card in zip(row, cards[start : start + PER_ROW], strict=False):
            with col:
                _card(card)


def _new_exam(user: dict, kind: str) -> None:
    mine = courses.list_courses(None if user["role"] == "admin" else user["username"])
    popover = st.popover(f"＋ New {kind}", width="stretch")
    with popover, st.form(f"new_{kind}", clear_on_submit=True, border=False):
        title = st.text_input(
            f"{kind.capitalize()} name",
            placeholder="e.g. Midterm Quiz 2" if kind == "exam" else "e.g. Homework 3",
        )
        options = [None, *[c["id"] for c in mine]]
        names = {c["id"]: courses.label(c) for c in mine} | {
            None: "No course (anyone marked sees it)"
        }
        course_id = st.selectbox("Course", options, format_func=names.get)
        if st.form_submit_button("Create", type="primary") and title.strip():
            st.session_state["exam_id"] = storage.create_exam(
                title, owner=user["username"], course_id=course_id, kind=kind
            )
            st.rerun()


def _attention(cards: list[dict]) -> None:
    pending = sum(c["pending"] for c in cards)
    waiting = sum(c["status"] in ("ready", "prepared") for c in cards)
    unpublished = sum(c["status"] == "marked" for c in cards)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(cards[0]["kind"].capitalize() + "s", len(cards))
    c2.metric("Waiting to be marked", waiting)
    c3.metric("Marked, not published", unpublished)
    c4.metric("Regrade requests", pending)


def _card(card: dict) -> None:
    label, kind = STATUS[card["status"]]
    with st.container(border=True):
        st.markdown(
            f'<div class="ag-card-title">{escape(card["title"])}</div>', unsafe_allow_html=True
        )
        facts = (
            f"{card['students']} students · {card['questions']} questions"
            if card["students"]
            else "Not read yet"
        )
        st.markdown(f'<div class="ag-card-meta">{facts}</div>', unsafe_allow_html=True)
        row = [(label, kind), (card["course"], "blue"), (card["model"], "violet")]
        if card["pending"]:
            row.append((f"{card['pending']} regrade request(s)", "red"))
        st.markdown(ui.chips(*row), unsafe_allow_html=True)
        if st.button("Open", key=f"open_{card['id']}", width="stretch"):
            st.session_state["exam_id"] = card["id"]
            st.rerun()

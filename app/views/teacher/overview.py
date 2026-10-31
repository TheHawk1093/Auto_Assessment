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
    head, action = st.columns([4, 1], vertical_alignment="bottom")
    with head:
        ui.page_header(
            "Your exams", "Upload, mark, review and publish. Pick up where you left off."
        )
    with action:
        _new_exam(user)
    exams_tab, courses_view = st.tabs([":material/description: Exams", ":material/groups: Courses"])
    with exams_tab:
        _exams(user)
    with courses_view:
        courses_tab.render()


def _exams(user: dict) -> None:
    cards = overview.for_owner(None if user["role"] == "admin" else user["username"])
    if not cards:
        st.info("No exams yet. Use “New exam” to create the first one.")
        return
    _attention(cards)
    for start in range(0, len(cards), PER_ROW):
        row = st.columns(PER_ROW)
        for col, card in zip(row, cards[start : start + PER_ROW], strict=False):
            with col:
                _card(card)


def _new_exam(user: dict) -> None:
    mine = courses.list_courses(None if user["role"] == "admin" else user["username"])
    popover = st.popover("＋ New exam", width="stretch")
    with popover, st.form("new_exam", clear_on_submit=True, border=False):
        title = st.text_input("Exam name", placeholder="e.g. ME5309 Quiz 2")
        options = [None, *[c["id"] for c in mine]]
        names = {c["id"]: courses.label(c) for c in mine} | {
            None: "No course (anyone marked sees it)"
        }
        course_id = st.selectbox("Course", options, format_func=names.get)
        if st.form_submit_button("Create", type="primary") and title.strip():
            st.session_state["exam_id"] = storage.create_exam(
                title, owner=user["username"], course_id=course_id
            )
            st.rerun()


def _attention(cards: list[dict]) -> None:
    pending = sum(c["pending"] for c in cards)
    waiting = sum(c["status"] in ("ready", "prepared") for c in cards)
    unpublished = sum(c["status"] == "marked" for c in cards)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Exams", len(cards))
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

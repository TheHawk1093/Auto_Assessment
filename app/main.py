"""Entry point: `.venv/Scripts/streamlit run app/main.py`.

Signs the user in, then shows the pages their role may use. To add a role or page: write
`views/<name>.py` with `render()` and add it to PAGES / ROLE_PAGES.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # so `app.` imports work

import streamlit as st  # noqa: E402

from app.ui import session, theme  # noqa: E402
from app.views import account, admin, notifications, student, teacher  # noqa: E402

PAGES = {"Admin": admin.render, "Teacher": teacher.render, "Student": student.render}
ROLE_PAGES = {"admin": ["Admin", "Teacher"], "teacher": ["Teacher"], "student": ["Student"]}


def main() -> None:
    """Set up the page, sign the user in and show the page for their role."""
    st.set_page_config(page_title="Autograde", page_icon="📝", layout="wide")
    theme.inject()
    user = session.current_user()
    if user is None:
        account.login()
        return
    pages = ROLE_PAGES[user["role"]]
    with st.sidebar:
        st.header("Autograde")
        account.sidebar_box(user)
        notifications.sidebar(user["username"])
        page = st.radio("Page", pages, horizontal=True) if len(pages) > 1 else pages[0]
        st.divider()
    PAGES[page]()


main()

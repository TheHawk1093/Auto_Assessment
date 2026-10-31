"""Teacher page: the overview of exams, or one exam's workspace.

Tabs are listed in `workspace.TABS`; add a tab there.
"""

from __future__ import annotations

import streamlit as st

from app.services import storage
from app.ui import session
from app.views.teacher import overview, workspace


def render() -> None:
    """Show the exam workspace if an exam is open, else the overview of exams."""
    user = session.current_user()
    exam_id = st.session_state.get("exam_id")
    owner = None if user["role"] == "admin" else user["username"]
    if exam_id not in {m["id"] for m in storage.list_exams(owner)}:
        st.session_state.pop("exam_id", None)  # deleted, or someone else's
        exam_id = None
    if exam_id:
        workspace.render(exam_id)
    else:
        overview.render()

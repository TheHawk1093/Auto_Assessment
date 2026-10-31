"""Student submissions: open a window, see who has submitted, add the work to the answers."""

from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

from app.services import storage, submissions
from app.ui import components as ui
from app.ui import session


def render_panel(exam_id: str) -> None:
    """The submission window, the list of who submitted, and the button that collects the work."""
    meta = storage.load_meta(exam_id)
    me = session.current_user()["username"]
    with st.container(border=True):
        st.markdown("**Student submissions**")
        st.caption("Students of the course hand in their work here. Then add it to the sheets.")
        if meta["course_id"] is None:
            st.info("Put this assignment in a course to take submissions.")
            return
        is_open, why = submissions.window(exam_id)
        st.markdown(
            ui.chips(("Open for submissions", "green") if is_open else (why, "neutral")),
            unsafe_allow_html=True,
        )
        _window_form(exam_id, meta, is_open, me)
        rows = submissions.roster_status(exam_id)
        if not rows:
            st.caption("Nobody is enrolled in the course yet.")
            return
        done = sum(r["handed_in"] for r in rows)
        st.markdown(f"**{done} of {len(rows)} submitted**")
        table = pd.DataFrame(
            [
                {
                    "student id": r["student_id"],
                    "name": r["name"],
                    "submitted": "yes" if r["handed_in"] else "no",
                    "when": r["at"].replace("T", " ")[:16],
                    "files": ", ".join(r["files"]),
                    "times": r["versions"] or "",
                }
                for r in rows
            ]
        )
        st.dataframe(table, hide_index=True, width="stretch")
        if st.button(
            "Add the work to the answer sheets", key=f"collect_{exam_id}", disabled=not done
        ):
            out = submissions.collect(exam_id, me)
            st.session_state[f"collected_{exam_id}"] = out
            st.rerun()
        out = st.session_state.pop(f"collected_{exam_id}", None)
        if out:
            st.success(
                f"{out['typed']} typed submission(s) added; {out['scanned']} handwritten one(s) "
                "added to the scans" + (" (read them next)." if out["scanned"] else ".")
            )
            for note in out["skipped"]:
                st.warning(note)


def _window_form(exam_id: str, meta: dict, is_open: bool, me: str) -> None:
    sub = meta["submissions"]
    with st.form(f"window_{exam_id}", border=False):
        left, right = st.columns([1, 2])
        current = date.fromisoformat(sub["deadline"]) if sub["deadline"] else None
        deadline = left.date_input(
            "Last day to submit (optional)", value=current, min_value=date.today()
        )
        note = right.text_area("What students should submit", sub["instructions"], height=90)
        formats = st.multiselect(
            "File types students may upload",
            submissions.ALL_GROUPS,
            default=sub["formats"] or submissions.ALL_GROUPS,
            format_func=lambda g: submissions.GROUPS[g][0],
        )
        open_btn, close_btn, _ = st.columns([1, 1, 3])
        if open_btn.form_submit_button(
            "Update" if sub["open"] else "Open submissions", type="primary"
        ):
            try:
                submissions.open_window(
                    exam_id, deadline.isoformat() if deadline else "", note, me, formats
                )
            except ValueError as e:
                st.error(str(e))
            else:
                st.rerun()
        if sub["open"] and close_btn.form_submit_button("Close submissions"):
            submissions.close_window(exam_id, me)
            st.rerun()

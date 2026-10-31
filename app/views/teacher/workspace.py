"""One exam: header, the path through the steps, and a tab per step."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import streamlit as st

from app.services import courses, jobs, models, regrades, storage
from app.ui import components as ui
from app.views.teacher import mark, publish, results, settings, upload
from app.views.teacher import regrades as regrades_tab


@dataclass(frozen=True)
class Tab:
    """One tab of the exam workspace: its name, icon, page and optional badge."""

    name: str
    icon: str  # a Material icon name
    render: Callable[[str], None]  # render(exam_id)
    badge: Callable[[str], str] | None = None  # text shown after the name when not empty

    def label(self, exam_id: str) -> str:
        """Return the tab title, with the badge in brackets when there is one."""
        badge = self.badge(exam_id) if self.badge else ""
        return f":material/{self.icon}: {self.name}" + (f" ({badge})" if badge else "")


def _pending(exam_id: str) -> str:
    n = regrades.pending_count(exam_id)
    return str(n) if n else ""


# To add a tab: write views/teacher/<name>.py with render(exam_id) and add a line here.
TABS = [
    Tab("Upload", "upload_file", upload.render),
    Tab("Settings", "tune", settings.render),
    Tab("Mark", "play_circle", mark.render),
    Tab("Results", "fact_check", results.render),
    Tab("Publish", "campaign", publish.render),
    Tab("Regrades", "forum", regrades_tab.render, _pending),
]
# How far along an exam is: the index of the step the teacher should do next.
NEXT_STEP = {"draft": 0, "ready": 1, "prepared": 2, "marked": 3, "published": 5}
STATUS_CHIP = {
    "draft": ("Needs files", "neutral"),
    "ready": ("Ready to prepare", "amber"),
    "prepared": ("Schemes written", "amber"),
    "marked": ("Marked", "green"),
    "published": ("Published", "blue"),
}


def render(exam_id: str) -> None:
    """Show one exam: header, the steps, and a tab for each step."""
    meta = storage.load_meta(exam_id)
    status = storage.exam_status(exam_id)
    back, head = st.columns([1, 6], vertical_alignment="center")
    if back.button("← All exams"):
        st.session_state.pop("exam_id", None)
        st.rerun()
    with head:
        text, kind = STATUS_CHIP[status]
        model = models.get(meta["model"]).label
        course = courses.label(courses.get(meta["course_id"]))
        ui.page_header(
            meta["title"], chip_row=ui.chips((text, kind), (course, "blue"), (model, "violet"))
        )
    ui.stepper(_steps(exam_id, status))
    for tab, t in zip(st.tabs([t.label(exam_id) for t in TABS]), TABS, strict=True):
        with tab:
            t.render(exam_id)
    _danger_zone(exam_id)


def _steps(exam_id: str, status: str) -> list[tuple[str, str, str]]:
    nxt = NEXT_STEP[status]
    steps = []
    for i, t in enumerate(TABS):
        state = "done" if i < nxt else "current" if i == nxt else "todo"
        steps.append((t.name, state, t.badge(exam_id) if t.badge else ""))
    return steps


def _danger_zone(exam_id: str) -> None:
    with st.expander("Rename this exam"), st.form(f"rename_{exam_id}", border=False):
        title = st.text_input("Title", storage.load_meta(exam_id)["title"])
        if st.form_submit_button("Rename"):
            try:
                storage.rename_exam(exam_id, title)
            except ValueError as e:
                st.error(str(e))
            else:
                st.rerun()
    with st.expander("Delete this exam"):
        sure = st.checkbox("Delete its files, marks and regrade requests", key=f"sure_{exam_id}")
        if st.button("Delete exam", disabled=not sure):
            if jobs.job_state(exam_id).get("state") == "running":
                st.error("Cancel the running job first.")
                return
            storage.delete_exam(exam_id)
            st.session_state.pop("exam_id", None)
            st.rerun()

"""Tab 1: the uploads. Exams take paper, rubric and answers; assignments take students' work."""

from __future__ import annotations

import streamlit as st

from app import config
from app.services import storage
from app.ui.widgets import upload_section
from app.views.teacher import scans as scans_view
from app.views.teacher import submissions as submissions_view

DOC = ["pdf", "docx", "txt", "md"]
CODE = ["py", "ipynb"]  # code questions and answers
SECTIONS = [
    dict(
        section="paper",
        label="Question paper (required)",
        help_="PDF, Word or text. Several files are read together.",
        multiple=True,
        zip_ok=False,
        types=[*DOC, *CODE],
        extra=frozenset(config.CODE_EXT),
    ),
    dict(
        section="reference",
        label="Rubric and model answers",
        help_="PDF, Word or text. Optional, but marking is best with one.",
        multiple=True,
        zip_ok=False,
        types=[*DOC, *CODE],
        extra=frozenset(config.CODE_EXT),
    ),
]
ANSWERS = dict(
    section="answers",
    label="Typed answer sheets",
    help_=(
        "One file per student (PDF, Word or text), or one zip. The roll number can be in the "
        "file name, for example 21ME004.docx, or written at the top of the sheet. "
        "Add a roster .csv (id, name) if you have one."
    ),
    multiple=True,
    zip_ok=True,
    types=[*DOC, "zip", "csv"],
    extra=frozenset({".csv"}),
)


def render(exam_id: str) -> None:
    """Show the upload boxes for this exam or assignment and whether the required files are in."""
    is_assignment = storage.load_meta(exam_id)["kind"] == "assignment"
    st.caption("Everything is saved. Nothing is marked until the Mark step.")
    for spec in SECTIONS:
        upload_section(exam_id, **(spec | ({"label": "Assignment brief (required)"}
                                           if is_assignment and spec["section"] == "paper"
                                           else {})))  # fmt: skip
    if is_assignment:
        submissions_view.render_panel(exam_id)
        scans_view.render_reader(exam_id)
    else:
        upload_section(exam_id, **ANSWERS)
        scans_view.render_box(exam_id)
    if storage.exam_status(exam_id) == "draft":
        need = "the brief and the students' work" if is_assignment else "the paper and the answers"
        st.warning(f"Required: {need}.")
    else:
        st.success("Required files are in. Continue to Settings, then Mark.")

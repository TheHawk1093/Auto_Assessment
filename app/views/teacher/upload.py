"""Tab 1: the three uploads. Boxes are listed in SECTIONS; edit the list to change them."""

from __future__ import annotations

import streamlit as st

from app.services import storage
from app.ui.widgets import upload_section
from app.views.teacher import scans as scans_view
from app.views.teacher import submissions as submissions_view

DOC = ["txt", "md", "docx", "pdf", "json"]
SECTIONS = [
    dict(
        section="paper",
        label="Question paper (required)",
        help_="One file: txt, md, docx, pdf or json.",
        multiple=False,
        zip_ok=False,
        types=DOC,
    ),
    dict(
        section="reference",
        label="Rubric and model answer",
        help_=(
            "Rubric and model answer, in one or many files, or a .zip of them. "
            "Optional, but the marking is best when one is given."
        ),
        multiple=True,
        zip_ok=True,
        types=[*DOC, "zip"],
    ),
    dict(
        section="answers",
        label="Student answer sheets (required)",
        help_=(
            "Typed answers: a .zip or several files, one file per student, with the roll number "
            "and name written at the top of each (the file name does not matter). A single "
            "answers .json also works. A roster .csv (student id, name, email) can be included. "
            "A scanned PDF with no text goes to the scanned sheets below by itself."
        ),
        multiple=True,
        zip_ok=True,
        types=[*DOC, "zip", "csv"],
        extra=frozenset({".csv"}),
    ),
]


def render(exam_id: str) -> None:
    """Show one upload box per section and whether the required files are in."""
    st.caption("Everything is saved to this exam. Nothing is marked until step 3.")
    for spec in SECTIONS:
        upload_section(exam_id, **spec)
    scans_view.render_box(exam_id)
    submissions_view.render_panel(exam_id)
    if storage.exam_status(exam_id) == "draft":
        st.warning(
            "The question paper and the student answers (typed, scanned or submitted) are required."
        )
    else:
        st.success("Required files are in. Continue to Settings, then Mark.")

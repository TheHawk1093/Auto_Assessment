"""Show text that may hold maths and any script.

Streamlit's own markdown draws maths written between dollar signs, so nothing is loaded from
outside. `rich_text` is for student answers and feedback (plain text, kept as written) and
`markdown` is for documents (schemes, reports).
Tables (`st.dataframe`) cannot render maths; show formulas as text, not in table cells.
"""

from __future__ import annotations

import streamlit as st

from app import text


def rich_text(value: str, *, empty: str = "(empty)") -> None:
    """Render plain text with maths drawn by Streamlit; the rest is shown as written."""
    value = text.normalize(value or "").strip()
    if not value:
        st.caption(empty)
        return
    st.markdown(text.plain_for_markdown(value))


def markdown(value: str) -> None:
    r"""Show a document with maths: `$x^2$`, `$$..$$`, and the `\(..\)` forms models write."""
    st.markdown(text.for_markdown(value))

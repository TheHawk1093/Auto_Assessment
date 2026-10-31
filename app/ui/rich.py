"""Show text that may hold maths and any script.

Uses KaTeX (served from app/static/katex, no CDN) plus a font stack that covers the Indic
scripts and the usual Windows/macOS/Linux fonts.

Use `rich_text` for student answers and feedback (plain text, kept as written). Use
`markdown` for documents (schemes, reports): Streamlit's own markdown already renders KaTeX.
Tables (`st.dataframe`) cannot render maths; keep formulas out of table cells.
"""

from __future__ import annotations

import html

import streamlit as st

from app import text

STATIC = "/app/static/katex"  # needs `enableStaticServing` (see .streamlit/config.toml)
FONTS = (
    'system-ui, "Segoe UI", "Noto Sans", "Noto Sans Devanagari", "Noto Sans Bengali", '
    '"Noto Sans Tamil", "Noto Sans Telugu", "Noto Sans Gujarati", "Noto Sans Kannada", '
    '"Noto Sans Malayalam", "Noto Sans Gurmukhi", "Nirmala UI", "Mangal", "Gautami", '
    '"Latha", "Kartika", sans-serif'
)
PAGE = """<!doctype html><meta charset="utf-8">
<link rel="stylesheet" href="{static}/katex.min.css">
<style>
 body {{ margin: 0; padding: 2px 4px; font: 15px/1.55 {fonts}; color: #1f2933;
        white-space: pre-wrap; overflow-wrap: anywhere; }}
 @media (prefers-color-scheme: dark) {{ body {{ color: #e5e7eb; }} }}
</style>
<body>{body}</body>
<script src="{static}/katex.min.js"></script>
<script src="{static}/auto-render.min.js"></script>
<script>
 renderMathInElement(document.body, {{
   throwOnError: false,
   delimiters: [
     {{left: "$$", right: "$$", display: true}}, {{left: "\\\\[", right: "\\\\]", display: true}},
     {{left: "\\\\(", right: "\\\\)", display: false}}, {{left: "$", right: "$", display: false}}
   ]
 }});
</script>"""


def rich_text(value: str, *, empty: str = "(empty)") -> None:
    """Render plain text with maths. Escaped, so student text can never run as HTML."""
    value = text.normalize(value or "").strip()
    if not value:
        st.caption(empty)
        return
    page = PAGE.format(static=STATIC, fonts=FONTS, body=html.escape(value))
    st.iframe(page, height="content")


def markdown(value: str) -> None:
    r"""Show a document with maths: `$x^2$`, `$$..$$`, and the `\(..\)` forms models write."""
    st.markdown(text.for_markdown(value))

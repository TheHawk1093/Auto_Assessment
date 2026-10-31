"""Reusable bits of page built as HTML: chips, page header, workflow stepper, score card.

Every piece of text is escaped here, so callers can pass student or teacher text safely. The
look comes from `ui/theme.py`.
"""

from __future__ import annotations

from html import escape

import streamlit as st

KINDS = ("neutral", "blue", "green", "amber", "red", "violet")


def chip(text: str, kind: str = "neutral") -> str:
    """Return a small coloured label as HTML; the text is escaped."""
    kind = kind if kind in KINDS else "neutral"
    return f'<span class="ag-chip {kind}">{escape(str(text))}</span>'


def chips(*items: tuple[str, str]) -> str:
    """(text, kind) pairs as one row of chips."""
    return "".join(chip(t, k) for t, k in items)


def page_header(title: str, subtitle: str = "", chip_row: str = "") -> None:
    """Show a page title, an optional subtitle and an optional row of chips."""
    sub = f"<p>{escape(subtitle)}</p>" if subtitle else ""
    st.markdown(
        f'<div class="ag-head"><h1>{escape(title)}</h1>{sub}{chip_row}</div>',
        unsafe_allow_html=True,
    )


def stepper(steps: list[tuple[str, str, str]]) -> None:
    """(name, state, badge) per step; state is done, current or todo. Shows the way through."""
    parts = []
    for i, (name, state, badge) in enumerate(steps, 1):
        dot = "✓" if state == "done" else str(i)
        extra = f'<span class="badge">{chip(badge, "amber")}</span>' if badge else ""
        parts.append(
            f'<div class="ag-step {state}"><span class="dot">{dot}</span>'
            f'<span class="name">{escape(name)}</span>{extra}</div>'
        )
    st.markdown(f'<div class="ag-steps">{"".join(parts)}</div>', unsafe_allow_html=True)


def tone(share: float) -> str:
    """good, mid or low for a share of the marks (0 to 1)."""
    return "good" if share >= 0.7 else "mid" if share >= 0.4 else "low"


def bar(share: float, tinted: bool = True) -> str:
    """Return a thin progress bar as HTML for a share of the marks (0 to 1)."""
    share = max(0.0, min(share, 1.0))
    cls = f"ag-bar {tone(share)}" if tinted else "ag-bar"
    return f'<div class="{cls}"><span style="width:{share * 100:.0f}%"></span></div>'


def score_card(label: str, total: float, out_of: float, note: str = "") -> None:
    """Show a large score with a bar, as total out of a maximum, and an optional note."""
    share = total / out_of if out_of else 0.0
    note_html = f'<div class="label" style="margin-top:10px">{escape(note)}</div>' if note else ""
    st.markdown(
        f'<div class="ag-score"><div class="label">{escape(label)}</div>'
        f'<span class="big">{total:g}</span> <span class="of">/ {out_of:g} '
        f"· {share * 100:.0f}%</span>{bar(share)}{note_html}</div>",
        unsafe_allow_html=True,
    )

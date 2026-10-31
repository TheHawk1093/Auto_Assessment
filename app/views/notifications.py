"""The sidebar's message list: unread count, the latest messages, and a button to clear them.

Refreshes itself every 20 seconds, so a published result or a regrade decision shows up without
anyone reloading the page.
"""

from __future__ import annotations

import html

import streamlit as st

from app.services import notifications


@st.fragment(run_every=20)
def sidebar(username: str) -> None:
    """Show 'Messages (n)' with the latest ones in an expander."""
    unread = notifications.unread_count(username)
    title = f"Messages ({unread})" if unread else "Messages"
    with st.expander(title, icon=":material/notifications:", expanded=bool(unread)):
        items = notifications.recent(username, 12)
        if not items:
            st.caption("No new messages.")
        for n in items:
            when = n["created"][:16].replace("T", " ")
            st.markdown(
                f"{html.escape(n['text'])}  \n<small>{when}</small>",
                unsafe_allow_html=True,
            )
        if unread and st.button("Mark all as read", key="notes_read"):
            notifications.mark_all_read(username)
            st.rerun()

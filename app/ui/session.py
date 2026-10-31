"""Who is signed in. Held in Streamlit's session state, so a browser refresh signs out."""

from __future__ import annotations

import streamlit as st


def current_user() -> dict | None:
    """{username, role, name} of the signed-in user, or None."""
    return st.session_state.get("user")


def sign_in(user: dict) -> None:
    """Remember the signed-in user for this browser session."""
    st.session_state["user"] = user


def sign_out() -> None:
    """Forget the user and everything else held in the session."""
    st.session_state.clear()


def student_id() -> str | None:
    """Return the signed-in student's unique id (roll number), or None.

    Falls back to the username for an account that predates student ids.
    """
    user = current_user()
    if not user or user["role"] != "student":
        return None
    return user.get("student_id") or user["username"]

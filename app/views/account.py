"""Sign-in, first-run admin setup, and the sidebar account box."""

from __future__ import annotations

import streamlit as st

from app.services import auth
from app.ui import components as ui
from app.ui import session


def login() -> None:
    """The sign-in form; on a fresh install, the form that creates the first admin."""
    _, centre, _ = st.columns([1, 1.4, 1])
    with centre:
        st.markdown("<div style='height:8vh'></div>", unsafe_allow_html=True)
        ui.page_header("Autograde", "Fair, fast marking with feedback students can learn from.")
        if not auth.has_users():
            _first_admin()
            return
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Sign in", type="primary", width="stretch"):
                user = auth.authenticate(username, password)
                if user:
                    session.sign_in(user)
                    st.rerun()
                st.error("Wrong username or password, or the account is disabled.")


def _first_admin() -> None:
    st.info("No accounts yet. Create the first administrator; it can then add teachers.")
    with st.form("first_admin"):
        username = st.text_input("Admin username")
        name = st.text_input("Name")
        password = st.text_input(
            f"Password (at least {auth.MIN_PASSWORD} characters)", type="password"
        )
        if st.form_submit_button("Create administrator", type="primary"):
            try:
                auth.create_user(username, "admin", name, password)
            except ValueError as e:
                st.error(str(e))
            else:
                session.sign_in(auth.authenticate(username, password))
                st.rerun()


def sidebar_box(user: dict) -> None:
    """Show the signed-in user, a change-password form and the sign-out button."""
    st.markdown(f"**{user['name'] or user['username']}**  \n{user['role']}")
    with st.expander("Change password"), st.form("change_password", clear_on_submit=True):
        old = st.text_input("Current password", type="password")
        new = st.text_input("New password", type="password")
        if st.form_submit_button("Change"):
            if not auth.authenticate(user["username"], old):
                st.error("The current password is wrong.")
            else:
                try:
                    auth.set_password(user["username"], new, by=user["username"])
                    st.success("Password changed.")
                except ValueError as e:
                    st.error(str(e))
    if st.button("Sign out"):
        session.sign_out()
        st.rerun()

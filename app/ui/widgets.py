"""Small reusable pieces of page. A view should read like a layout; the fiddly bits live here."""

from __future__ import annotations

import streamlit as st

from app.services import jobs, scans, storage


def upload_section(
    exam_id: str,
    section: str,
    label: str,
    help_: str,
    *,
    multiple: bool,
    zip_ok: bool,
    types: list[str],
    extra: frozenset[str] = frozenset(),
) -> None:
    """A bordered box: what is saved, an uploader, Save and Remove. Saving replaces the section."""
    nonce_key = f"nonce_{exam_id}_{section}"
    nonce = st.session_state.setdefault(nonce_key, 0)  # a new key empties the uploader
    with st.container(border=True):
        st.markdown(f"**{label}**")
        st.caption(help_)
        current = storage.uploaded_files(exam_id, section)
        if current:
            shown = ", ".join(p.name for p in current[:8])
            more = f" and {len(current) - 8} more" if len(current) > 8 else ""
            st.success(f"{len(current)} file(s) saved: {shown}{more}")
        picked = st.file_uploader(
            label,
            type=types,
            accept_multiple_files=multiple,
            key=f"up_{exam_id}_{section}_{nonce}",
            label_visibility="collapsed",
        )
        picked = picked if isinstance(picked, list) else ([picked] if picked else [])
        left, right = st.columns(2)
        if left.button("Save files", key=f"save_{section}", disabled=not picked):
            saved, skipped = storage.save_uploads(
                exam_id, section, [(f.name, f.getvalue()) for f in picked], zip_ok, set(extra)
            )
            if section == "answers":  # a PDF with no text is a scan: it is read like a photo
                moved = scans.divert_unreadable_pdfs(exam_id)
                if moved:
                    st.session_state[f"moved_{exam_id}"] = moved
            st.session_state[nonce_key] = nonce + 1
            st.session_state[f"skipped_{exam_id}_{section}"] = skipped
            st.rerun()
        if current and right.button("Remove all", key=f"clear_{section}"):
            storage.clear_section(exam_id, section)
            st.rerun()
        moved = st.session_state.get(f"moved_{exam_id}") if section == "answers" else None
        if moved:
            st.info(f"{', '.join(moved)}: no text layer, so moved to the scanned sheets below.")
        skipped = st.session_state.get(f"skipped_{exam_id}_{section}")
        if skipped:
            st.warning(f"Skipped (unsupported type): {', '.join(skipped[:10])}")


def job_banner(exam_id: str) -> None:
    """One line on the exam's job: running, finished, failed or cancelled, with the log."""
    state = jobs.job_state(exam_id)
    if not state:
        st.caption("No job has run for this exam yet.")
        return
    what = {
        "schemes": "Preparing schemes",
        "mark": "Marking",
        "scan": "Reading scanned sheets",
        "recheck": "Rechecking an answer",
    }.get(state["kind"], state["kind"])
    if state["state"] == "running":
        st.info(f"{what}… started {state['started']}")
    else:
        done = {"done": "finished", "failed": "failed", "cancelled": "was cancelled"}
        st.write(
            f"{what} {done[state['state']]} at {state.get('finished', '')}. {state.get('note', '')}"
        )
    with st.expander("Log", expanded=state["state"] == "failed"):
        st.code(jobs.log_tail(exam_id) or "(empty)", language=None)


def original_pages(exam_id: str, student_id: str, *, expanded: bool = False) -> None:
    """Show the student's original handwritten pages, when their answer was read from a scan.

    The page is the ground truth. The text beside it was read from it for the marking pipeline
    only, and can contain mistakes.
    """
    pages = scans.pages_for(exam_id, student_id)
    if not pages:
        return
    with st.expander(f"Original handwritten sheet ({len(pages)} page(s))", expanded=expanded):
        st.caption(
            "This is what the student wrote. The text shown elsewhere was read from it so the "
            "pipeline can mark it; if they differ, the page is right."
        )
        for page in pages:
            st.image(str(page), caption=page.name, width="stretch")

"""Scanned and handwritten sheets: the upload box (Upload tab) and the check-what-was-read panel.

The panel is on the Mark tab. A scan is read into text once; the teacher can correct the text
before marking.
"""

from __future__ import annotations

import streamlit as st

from app.services import jobs, models, scans, storage
from app.ui import components as ui

TYPES = ["png", "jpg", "jpeg", "webp", "pdf", "zip"]


def render_box(exam_id: str) -> None:
    """Upload photos or scans, choose who reads them, and start reading."""
    nonce_key = f"nonce_{exam_id}_scans"
    nonce = st.session_state.setdefault(nonce_key, 0)
    with st.container(border=True):
        st.markdown("**Handwritten or scanned answer sheets**")
        st.caption(
            "Photos (png, jpg, webp) or PDFs, one sheet per student, or a .zip of them. Pages of "
            "one sheet can be named `name_p1`, `name_p2`; a PDF is split into its pages. Each "
            "sheet is read into text that you can check and correct on the Mark tab. The student "
            "writes their name and roll number at the top."
        )
        picked = st.file_uploader(
            "Scans", type=TYPES, accept_multiple_files=True, label_visibility="collapsed",
            key=f"up_{exam_id}_scans_{nonce}",
        )  # fmt: skip
        if st.button("Add these sheets", key=f"add_scans_{exam_id}", disabled=not picked):
            added, skipped = scans.add(exam_id, [(f.name, f.getvalue()) for f in picked])
            st.session_state[nonce_key] = nonce + 1
            st.session_state[f"scan_note_{exam_id}"] = (added, skipped)
            st.rerun()
        added, skipped = st.session_state.pop(f"scan_note_{exam_id}", ([], []))
        if added:
            st.success(f"Added {len(added)} sheet(s).")
        if skipped:
            st.warning("Skipped: " + "; ".join(skipped[:8]))
        _sheets_and_reader(exam_id)


def _sheets_and_reader(exam_id: str) -> None:
    rows = scans.rows(exam_id)
    if not rows:
        return
    unread = [r for r in rows if not r["read"]]
    chips = ui.chips(
        (f"{len(rows)} sheet(s)", "blue"),
        (f"{len(unread)} not read yet", "amber" if unread else "green"),
    )
    st.markdown(chips, unsafe_allow_html=True)
    meta = storage.load_meta(exam_id)
    options = models.READERS
    ids = [o.id for o in options]
    current = meta["reader"] if meta["reader"] in ids else models.DEFAULT_READER
    labels = {
        o.id: o.label + ("" if models.reader_availability(o)[0] else " (not available)")
        for o in options
    }
    pick = st.selectbox(
        "Who reads the handwriting", ids, index=ids.index(current), format_func=labels.get,
        key=f"reader_{exam_id}",
    )  # fmt: skip
    if pick != current:
        storage.set_reader(exam_id, pick)
    reader = models.get_reader(pick)
    ok, why = models.reader_availability(reader)
    st.caption(reader.blurb if ok else f"{reader.blurb} Not usable now: {why}")
    busy = jobs.running_exam()
    if st.button(
        "Read the scanned sheets",
        key=f"read_{exam_id}",
        disabled=bool(busy) or not unread or not ok,
    ):
        try:
            jobs.start_scan(exam_id)
        except RuntimeError as e:
            st.error(str(e))
        else:
            st.rerun()
    if busy:
        st.caption("A job is running; start reading when it finishes.")


def render_review(exam_id: str) -> None:
    """Each scanned sheet beside what was read from it, editable."""
    rows = scans.rows(exam_id)
    if not rows:
        return
    st.subheader("Scanned sheets: check what was read")
    st.caption(
        "Compare the page with the text. `[?word?]` marks a spot the reader was unsure of. "
        "Fix any mistake and save; the marking uses exactly this text."
    )
    for r in sorted(rows, key=lambda r: (r["read"], -r["unsure"], r["sheet"])):
        if not r["read"]:
            state = "Not read yet"
        else:
            state = f"{r['words']} words" + (f", {r['unsure']} unsure" if r["unsure"] else "")
        with st.expander(f"{r['sheet']} · {state}", expanded=bool(r["unsure"]) and r["read"]):
            if r["error"]:
                st.error(f"The reader failed: {r['error']}")
            if r["known"]:
                st.caption(f"Submitted by {r['known']['student_id']} (known from the account).")
            left, right = st.columns(2)
            with left:
                for page in r["pages"]:
                    st.image(str(page), caption=page.name, width="stretch")
            with right:
                if not r["read"]:
                    st.info("Use 'Read the scanned sheets' on the Upload tab.")
                else:
                    key = f"tx_{exam_id}_{r['sheet']}"
                    text = st.text_area("What was read", r["text"], height=420, key=key)
                    a, b, c = st.columns(3)
                    if a.button(
                        "Save corrections",
                        key=f"txs_{exam_id}_{r['sheet']}",
                        disabled=text == r["text"],
                    ):
                        scans.save_transcript(exam_id, r["sheet"], text)
                        st.rerun()
                    if b.button("Read again", key=f"txr_{exam_id}_{r['sheet']}"):
                        scans.forget_read(exam_id, r["sheet"])
                        st.rerun()
                    if c.button("Remove sheet", key=f"txd_{exam_id}_{r['sheet']}"):
                        scans.remove_sheet(exam_id, r["sheet"])
                        st.rerun()

"""Tab 3: prepare (read the files, write the marking schemes), then mark."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services import identity, jobs, scans, storage
from app.services import results as res
from app.ui import components as ui
from app.ui import rich
from app.ui.widgets import job_banner
from app.views.teacher import scans as scans_view


def render(exam_id: str) -> None:
    """Show the Prepare and Mark buttons, job progress and who wrote which sheet."""
    busy = jobs.running_exam()
    ready = storage.exam_status(exam_id) != "draft"
    st.markdown(
        "**Prepare** reads your files and writes a marking scheme for every question, so you "
        "can check them. **Mark** then marks every student and writes the feedback."
    )
    a, b, c = st.columns(3)
    unread = scans.unread(exam_id)
    ready = ready and not unread
    if a.button("Prepare (read files, write schemes)", disabled=bool(busy) or not ready):
        _start(exam_id, schemes_only=True)
    held = identity.blocking(exam_id)
    allow = storage.load_meta(exam_id)["settings"]["allow_unresolved"]
    gated = bool(held) and not allow
    if b.button("Mark all answers", type="primary", disabled=bool(busy) or not ready or gated):
        _start(exam_id, schemes_only=False)
    if busy == exam_id and c.button("Cancel the running job"):
        jobs.cancel(exam_id)
        st.rerun()
    if busy and busy != exam_id:
        st.warning(f"Another exam ({busy}) is being marked. Only one job can run at a time.")
    if unread:
        st.warning(
            f"{len(unread)} scanned sheet(s) have not been read yet. Use 'Read the scanned sheets' "
            "on the Upload tab first."
        )
    if gated:
        st.warning(
            f"{len(held)} sheet(s) cannot be attributed to a student yet. Choose the student for "
            "each below, then mark. (Settings has an option to mark the rest anyway.)"
        )
    _status(exam_id)
    scans_view.render_review(exam_id)
    _identity(exam_id)
    info = res.intake(exam_id)
    if info:
        _intake_summary(exam_id, info)


def _start(exam_id: str, schemes_only: bool) -> None:
    try:
        jobs.start(exam_id, schemes_only)
    except RuntimeError as e:
        st.error(str(e))
        return
    st.rerun()


@st.fragment(run_every=3)
def _status(exam_id: str) -> None:
    """Refreshes itself every 3 s; when a job ends it reruns the page so the summary appears."""
    state = jobs.job_state(exam_id)
    if state.get("state") == "running":
        done, total = res.progress(exam_id)
        if state["kind"] == "mark" and total:
            st.progress(min(done / total, 1.0), text=f"Marking: {done} of {total} answers")
        st.session_state["was_running"] = True
    elif st.session_state.pop("was_running", False):
        st.rerun()
    job_banner(exam_id)


def _intake_summary(exam_id: str, info: dict) -> None:
    paper = info["paper"]
    st.subheader("What was read")
    questions = paper["questions"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Questions", len(questions))
    m2.metric("Total marks", f"{sum(q['max_mark'] for q in questions):g}")
    m3.metric("Students", len(info["students"]))
    for w in info.get("warnings", []):
        st.warning(w)
    st.dataframe(
        pd.DataFrame(
            [
                {
                    "id": q["id"],
                    "marks": q["max_mark"],
                    "kind": q.get("kind", ""),
                    "question": q["text"][:140],
                }
                for q in questions
            ]
        ),
        hide_index=True,
        width="stretch",
    )
    with st.expander("Students found"):
        st.write(", ".join(info["students"]))
    rules = info.get("rules", {})
    if rules.get("found"):
        with st.expander("Rules read from the paper and rubric"):
            st.json({k: v for k, v in rules.items() if v not in (None, False, "unstated", [])})
    schemes = res.schemes_text(exam_id)
    if schemes:
        with st.expander("Marking schemes (check these before marking)"):
            rich.markdown(schemes)


STATE_CHIP = {
    "ok": ("Matched", "green"),
    "check": ("Please check", "amber"),
    "unresolved": ("Unknown", "red"),
}
HOW = {
    "roll+name": "roll number and name agree",
    "roll": "roll number",
    "roll_corrected": "roll number, one character corrected",
    "name": "name only",
    "model": "chosen by the model from the candidates",
    "filename": "file name only",
    "teacher": "set by you",
}


def _identity(exam_id: str) -> None:
    """Show who the pipeline decided wrote each sheet, with a way to choose.

    Read from the sheet and checked against the student database. What it could not settle is
    listed first.
    """
    entries = identity.report(exam_id)
    if not entries:
        return
    st.subheader("Who wrote which sheet")
    st.caption(
        "The roll number written on each sheet is matched to the student database, with the name "
        "used to settle doubt. File names are not relied on."
    )
    order = {"unresolved": 0, "check": 1, "ok": 2}
    for e in sorted(entries, key=lambda e: order[e["status"]]):
        _sheet(exam_id, e)


def _sheet(exam_id: str, e: dict) -> None:
    label, kind = STATE_CHIP[e["status"]]
    who = f"{e['student_id']} · {e['name']}" if e["student_id"] else "not identified"
    with st.container(border=True):
        left, mid, right = st.columns([2, 3, 2], vertical_alignment="center")
        left.markdown(f"**{e['source']}**")
        claimed = (e["claimed"]["roll"], e["claimed"]["name"])
        said = " · ".join(x for x in claimed if x) or "nothing readable"
        mid.markdown(f"On the sheet: {said}  \nMatched to: **{who}**")
        right.markdown(ui.chip(label, kind) + _how(e), unsafe_allow_html=True)
        if e["flags"]:
            st.caption("Look at: " + ", ".join(e["flags"]))
        if e["status"] == "ok" and e["method"] != "teacher":
            return
        options = identity.choices(exam_id, e)
        ids = [sid for sid, _ in options]
        labels = dict(options)
        default = ids.index(e["student_id"]) if e["student_id"] in ids else None
        pick = st.selectbox(
            "This sheet belongs to", ids, index=default, format_func=labels.get,
            key=f"who_{exam_id}_{e['source']}", placeholder="Choose a student",
        )  # fmt: skip
        if st.button("Use this student", key=f"fix_{exam_id}_{e['source']}", disabled=pick is None):
            identity.set_fix(exam_id, e["source"], pick)
            st.rerun()


def _how(e: dict) -> str:
    text = HOW.get(e["method"], "")
    return f"<br><small>{text}</small>" if text else ""

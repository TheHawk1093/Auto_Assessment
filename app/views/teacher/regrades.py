"""Tab 6: the regrade inbox. The teacher decides; upholding changes the mark.

For each request the teacher can decide alone, or first have the pipeline grade that answer
autonomously with a note and read what it proposes. The pipeline only proposes.
"""

from __future__ import annotations

import streamlit as st

from app.services import jobs, models, recheck, regrades, report, storage
from app.ui import rich, session


def render(exam_id: str) -> None:
    """Show the regrade requests waiting for a decision, and decided ones."""
    if not storage.load_meta(exam_id)["published"]:
        st.info("Students can ask for regrades once you publish the results.")
        return
    pending = regrades.list_requests(exam_id, status="pending")
    decided = [r for r in regrades.list_requests(exam_id) if r["status"] != "pending"]
    st.subheader(f"Waiting for you ({len(pending)})")
    if not pending:
        st.success("No requests are waiting.")
    for req in pending:
        _request(exam_id, req)
    with st.expander(f"Decided ({len(decided)})"):
        for r in decided:
            change = f" {r['old_mark']:g} → {r['new_mark']:g}" if r["status"] == "upheld" else ""
            head = f"**#{r['id']}** {r['student']} Q{r['question']}: {r['status']}{change}"
            st.markdown(f"{head}  \n_{r['reply']}_")


def _request(exam_id: str, req: dict) -> None:
    row = next(x for x in report.rows(exam_id, req["student"]) if x["question"] == req["question"])
    now = f"{row['mark']:g} / {row['max']:g}"
    title = f"#{req['id']} · {req['student']} · question {req['question']} · now {now}"
    with st.expander(title, expanded=True):
        st.caption(f"{regrades.KINDS[req['kind']]} · asked {req['created']}")
        st.markdown("**The student's reason**")
        rich.rich_text(req["reason"])
        left, right = st.columns(2)
        left.caption("Their answer")
        with left:
            rich.rich_text(row["answer"])
        right.caption("The feedback they were given")
        with right:
            rich.rich_text(row["feedback"], empty="(none)")
        key = f"rg_{req['id']}"
        _recheck(exam_id, req, row, key)
        uphold = st.radio(
            "Decision", ["Reject", "Change the mark"], horizontal=True, key=f"{key}_d"
        )
        new_mark = None
        if uphold == "Change the mark":
            new_mark = st.number_input("New mark", 0.0, float(row["max"]), float(row["mark"]),
                                       step=0.5, key=f"{key}_m")  # fmt: skip
        reply = st.text_area("Reply to the student", key=f"{key}_r")
        if st.button("Send decision", key=f"{key}_b", type="primary"):
            try:
                regrades.decide(req["id"], uphold == "Change the mark", reply,
                                session.current_user()["username"], new_mark)  # fmt: skip
            except ValueError as e:
                st.error(str(e))
            else:
                st.rerun()


def _use_proposal(key: str, prop: dict, old_mark: float) -> None:
    """Fill the decision form from the pipeline's proposal; the teacher still edits and sends."""
    changed = abs(prop["mark"] - old_mark) > 1e-9
    st.session_state[f"{key}_d"] = "Change the mark" if changed else "Reject"
    st.session_state[f"{key}_m"] = float(prop["mark"])
    st.session_state[f"{key}_r"] = prop["feedback"]


def _recheck(exam_id: str, req: dict, row: dict, key: str) -> None:
    """Optional: have the pipeline grade this answer again, with a note, and read its proposal."""
    with st.container(border=True):
        st.subheader("Grade autonomously")
        st.caption(
            "It marks this one answer again with your note, using the exam's marking scheme. It "
            "only proposes: you read it and decide. The student's reason is not sent to it."
        )
        meta = storage.load_meta(exam_id)
        ids = [o.id for o in models.usable()]
        if not ids:
            st.warning("No AI model is available right now.")
        else:
            default = ids.index(meta["model"]) if meta["model"] in ids else 0
            model = st.selectbox(
                "Marked by", ids, index=default, format_func=lambda i: models.get(i).label,
                key=f"{key}_model",
            )  # fmt: skip
            note = st.text_area(
                "What should it look at?", key=f"{key}_note", height=70,
                placeholder="e.g. Accept either method; check the unit conversion in step 2.",
            )  # fmt: skip
            running = recheck.running_for(exam_id)
            busy = jobs.running_exam()
            if st.button(
                "Grade autonomously", key=f"{key}_ask", type="primary", disabled=bool(busy)
            ):
                try:
                    recheck.ask(exam_id, req["id"], model, note, session.current_user()["username"])
                except (ValueError, RuntimeError) as e:
                    st.error(str(e))
                else:
                    st.rerun()
            if busy and running != req["id"]:
                st.caption("Another job is running; this can start when it finishes.")
            if running == req["id"]:
                _recheck_wait(exam_id)
        prop = recheck.proposal(exam_id, req["id"])
        if prop:
            old = float(row["mark"])
            st.markdown(
                f"**Proposal:** {prop['mark']:g} / {prop['max']:g} (now {old:g}) · {prop['model']}"
            )
            rich.rich_text(prop["feedback"], empty="(no feedback)")
            if prop["note"]:
                st.caption(f"Your note was: {prop['note']}")
            st.button(
                "Use this proposal in my decision below", key=f"{key}_use",
                on_click=_use_proposal, args=(key, prop, old),
            )  # fmt: skip


@st.fragment(run_every=3)
def _recheck_wait(exam_id: str) -> None:
    """Show that the recheck is running; when it ends, reload the page so the proposal appears."""
    if jobs.job_state(exam_id).get("state") == "running":
        st.info("The pipeline is looking at this answer again…")
        st.session_state["recheck_ran"] = True
    elif st.session_state.pop("recheck_ran", False):
        st.rerun()

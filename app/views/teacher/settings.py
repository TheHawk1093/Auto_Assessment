"""Tab 2: marking settings. Widgets come from services/settings_spec.FIELDS, laid out by `group`."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services import models, settings_spec, storage
from app.services import results as res
from app.services.settings_spec import Field

CUSTOM_STEP = "Custom step (enter marks)"


def render(exam_id: str) -> None:
    """Show the model card and the marking settings, saving changes to the exam."""
    _model_card(exam_id)
    st.subheader("How to mark")
    saved = storage.load_meta(exam_id)["settings"]
    info = res.intake(exam_id)
    if info.get("rules", {}).get("found"):
        st.info("Rules in your paper and rubric are applied. Anything set here overrides them.")
    values: dict = {}
    left, right = st.columns(2)
    values.update(_part_marks(left, saved, exam_id))
    values["strictness"] = _widget(settings_spec.BY_KEY["strictness"], saved["strictness"],
                                   right, exam_id, info)  # fmt: skip
    values.update(_best_of(st, saved, exam_id))
    for f in settings_spec.FIELDS:
        if f.group == "notes" and f.key != "struck_out":
            values[f.key] = _widget(f, saved[f.key], st, exam_id, info)
    values["struck_out"] = _crossed_out(saved["struck_out"], exam_id)
    toggles = [f for f in settings_spec.FIELDS if f.group == "toggles"]
    for col, f in zip(st.columns(len(toggles)), toggles, strict=True):
        values[f.key] = _widget(f, saved[f.key], col, exam_id, info)
    if st.button("Save settings", type="primary"):
        storage.update_settings(exam_id, **values)
        st.success("Saved.")


def _part_marks(where, saved: dict, exam_id: str) -> dict:
    """One choice for how part marks are given, with a custom step as the last option."""
    f = settings_spec.BY_KEY["granularity"]
    labels = [*f.options, CUSTOM_STEP]
    if saved["mark_step"]:
        index = len(labels) - 1
    else:
        index = list(f.options.values()).index(saved["granularity"]) if (
            saved["granularity"] in f.options.values()) else 0  # fmt: skip
    pick = where.selectbox(f.label, labels, index=index, key=f"set_{exam_id}_granularity")
    if pick != CUSTOM_STEP:
        return {"granularity": f.options[pick], "mark_step": None}
    step = where.number_input("Marks come in multiples of", min_value=0.05, step=0.05,
                              value=float(saved["mark_step"] or 0.5),
                              key=f"set_{exam_id}_mark_step")  # fmt: skip
    return {"granularity": None, "mark_step": step}


def _best_of(where, saved: dict, exam_id: str) -> dict:
    """'Answer any N' papers: a tick, then how many questions count."""
    on = where.checkbox("Only the best few questions count (answer any N)",
                        value=bool(saved["count_best"]), key=f"set_{exam_id}_best_on")  # fmt: skip
    if not on:
        return {"count_best": None}
    n = where.number_input("How many questions count", min_value=1, step=1,
                           value=int(saved["count_best"] or 1),
                           key=f"set_{exam_id}_count_best")  # fmt: skip
    return {"count_best": int(n)}


def _crossed_out(saved: list, exam_id: str) -> list[str]:
    """A small table of questions a student crossed out; they are not marked."""
    rows = [x.split("=", 1) for x in saved if "=" in x]
    df = pd.DataFrame(rows, columns=["student", "question"])
    with st.expander("A student crossed out a question?"):
        st.caption("List the student and question. It is not marked.")
        edited = st.data_editor(df, num_rows="dynamic", hide_index=True, width="stretch",
                                key=f"set_{exam_id}_struck")  # fmt: skip
    return [f"{r.student.strip()}={r.question.strip()}" for r in edited.itertuples()
            if str(r.student or "").strip() and str(r.question or "").strip()]


def _widget(f: Field, value, where, exam_id: str, info: dict):
    """Draw one field in `where` (a column or `st`) and return what the teacher chose."""
    key = f"set_{exam_id}_{f.key}"
    if f.kind == "select":
        options = list(f.options)
        index = list(f.options.values()).index(value) if value in f.options.values() else 0
        return f.options[where.selectbox(f.label, options, index=index, help=f.help or None,
                                         key=key)]  # fmt: skip
    if f.kind in ("number", "int"):
        num = int if f.kind == "int" else float
        step = 1 if f.kind == "int" else 0.1
        got = where.number_input(f.label, min_value=num(0), step=num(step), value=num(value or 0),
                                 help=f.help or None, key=key)  # fmt: skip
        return num(got) or None
    if f.kind == "textarea":
        return where.text_area(f.label, value=value, placeholder=f.placeholder, key=key)
    if f.kind == "lines":
        text = where.text_area(f.label, value="\n".join(value), placeholder=f.placeholder,
                               help=f.help or None, key=key)  # fmt: skip
        return [x.strip() for x in text.splitlines() if "=" in x]
    if f.kind == "bool":
        return where.checkbox(f.label, value=value, key=key)
    if f.kind == "per_question":
        return _per_question(f, value, exam_id, info)
    raise ValueError(f"No widget for field kind {f.kind!r}")


def _per_question(f: Field, value: dict, exam_id: str, info: dict) -> dict:
    qids = [q["id"] for q in info.get("paper", {}).get("questions", [])]
    with st.expander(f.label):
        if not qids:
            st.caption("Available after step 3 has read the paper (press Prepare).")
            return value
        df = pd.DataFrame({"question": qids, "note": [value.get(q, "") for q in qids]})
        edited = st.data_editor(df, hide_index=True, disabled=["question"], width="stretch",
                                key=f"set_{exam_id}_{f.key}")  # fmt: skip
        return {r.question: r.note for r in edited.itertuples() if r.note}


def _model_card(exam_id: str) -> None:
    """Show which AI marks this exam and let the teacher change it.

    Only options the administrator allows and this machine can run are offered; the others are
    listed with the reason.
    """
    meta = storage.load_meta(exam_id)
    st.subheader("AI model")
    usable = models.usable()
    if not usable:
        st.error("No AI model is available. Ask the administrator to enable one.")
        return
    labels = {o.id: o.label for o in usable}
    current = meta["model"] if meta["model"] in labels else usable[0].id
    with st.container(border=True):
        pick = st.selectbox(
            "Marks this exam with",
            list(labels),
            index=list(labels).index(current),
            format_func=labels.get,
            key=f"model_{exam_id}",
        )
        option = models.get(pick)
        st.caption(option.blurb)
        if pick != meta["model"]:
            if storage.exam_status(exam_id) != "draft":
                st.info("Prepare will run again for the new model.")
            if st.button("Use this model", type="primary", key=f"use_model_{exam_id}"):
                storage.set_model(exam_id, pick)
                st.rerun()
        _reader_card(exam_id, meta)
        with st.expander("Which should I pick?"):
            for o in usable:
                st.markdown(f"**{o.label}**: {o.use} {o.price}")
            for r in models.READERS:
                st.markdown(f"**{r.label}**: {r.use} {r.price}")


def _reader_card(exam_id: str, meta: dict) -> None:
    """Pick the model that reads handwritten pages (used only for scanned or photographed work)."""
    ids = [o.id for o in models.READERS]
    current = meta["reader"] if meta["reader"] in ids else models.DEFAULT_READER
    labels = {
        o.id: o.label + ("" if models.reader_availability(o)[0] else " (not available)")
        for o in models.READERS
    }
    pick = st.selectbox(
        "Reads handwriting with", ids, index=ids.index(current), format_func=labels.get,
        key=f"settings_reader_{exam_id}",
    )  # fmt: skip
    if pick != current:
        storage.set_reader(exam_id, pick)
        st.rerun()
    st.caption(models.get_reader(pick).blurb)

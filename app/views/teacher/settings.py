"""Tab 2: marking settings. Widgets come from services/settings_spec.FIELDS, laid out by `group`."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services import models, settings_spec, storage
from app.services import results as res
from app.services.settings_spec import Field
from app.ui import components as ui

# Which fields sit in which column of the page; add a group name to a Field to move it here.
MARKS_COLUMNS = (("granularity", "mark_step"), ("strictness", "count_best"))


def render(exam_id: str) -> None:
    """Show the model card and the marking settings, saving changes to the exam."""
    _model_card(exam_id)
    st.subheader("How to mark")
    saved = storage.load_meta(exam_id)["settings"]
    info = res.intake(exam_id)
    if info.get("rules", {}).get("found"):
        st.info(
            "Rules read from your paper and rubric are applied automatically. "
            "Anything you set here overrides them."
        )
    values: dict = {}
    for col, keys in zip(st.columns(len(MARKS_COLUMNS)), MARKS_COLUMNS, strict=True):
        for key in keys:
            values[key] = _widget(settings_spec.BY_KEY[key], saved[key], col, exam_id, info)
    for f in settings_spec.FIELDS:
        if f.group == "notes":
            values[f.key] = _widget(f, saved[f.key], st, exam_id, info)
    toggles = [f for f in settings_spec.FIELDS if f.group == "toggles"]
    for col, f in zip(st.columns(len(toggles)), toggles, strict=True):
        values[f.key] = _widget(f, saved[f.key], col, exam_id, info)
    if st.button("Save settings", type="primary"):
        storage.update_settings(exam_id, **values)
        st.success("Saved.")


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
        st.markdown(
            ui.chips(
                (models.TIER[option.tier], "blue"),
                (models.COST[option.cost], "green" if option.cost == "free" else "amber"),
            ),
            unsafe_allow_html=True,
        )
        st.caption(option.blurb)
        if pick != meta["model"]:
            if storage.exam_status(exam_id) != "draft":
                st.info(
                    "A different model writes its own marking schemes, so Prepare will run again."
                )
            if st.button("Use this model", type="primary", key=f"use_model_{exam_id}"):
                storage.set_model(exam_id, pick)
                st.rerun()
        locked = [(o, models.availability(o)[1]) for o in models.catalogue() if o not in usable]
        if locked:
            with st.expander("Other models (not available)"):
                for o, why in locked:
                    st.markdown(f"**{o.label}**  \n{why}")

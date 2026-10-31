"""Tab 4: marks, flagged answers, one answer in detail (with mark override), and downloads."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services import exports, grades, report
from app.services import results as res
from app.ui import rich, session
from app.ui.widgets import original_pages


def render(exam_id: str) -> None:
    """Show marks, flagged answers, one answer in detail and downloads."""
    if not res.has_results(exam_id):
        st.info("Results appear here once marking has finished (step 3).")
        return
    marks = grades.marks_table(exam_id)
    rs = res.results(exam_id)
    flagged = res.flagged_table(rs)
    _headline(exam_id, marks, flagged)
    _downloads(exam_id)
    st.subheader("Marks")
    st.caption("Includes any marks you changed.")
    _marks_table(exam_id, marks)
    _flagged(flagged)
    _one_answer(exam_id, rs)


def _headline(exam_id: str, marks: pd.DataFrame, flagged: pd.DataFrame) -> None:
    total = "counted_total" if "counted_total" in marks else "total"
    first = marks["student"].iloc[0]
    out_of = grades.student_total(exam_id, first, grades.final_marks(exam_id)[first])[1]
    cols = st.columns(4)
    cols[0].metric("Students", len(marks))
    cols[1].metric("Average", f"{marks[total].mean():.1f} / {out_of:g}")
    cols[2].metric("Highest / lowest", f"{marks[total].max():g} / {marks[total].min():g}")
    cols[3].metric("To check", len(flagged))


def _marks_table(exam_id: str, marks: pd.DataFrame) -> None:
    total = "counted_total" if "counted_total" in marks else "total"
    out_of = (
        marks["counted_out_of"]
        if "counted_out_of" in marks
        else pd.Series(grades.paper(exam_id).total, index=marks.index)
    )
    shown = marks.copy()
    shown.insert(1, "score", (marks[total] / out_of * 100).round(0))
    st.dataframe(
        shown,
        hide_index=True,
        width="stretch",
        column_config={
            "score": st.column_config.ProgressColumn(
                "Score", format="%d%%", min_value=0, max_value=100
            )
        },
    )
    with st.expander("Score distribution"):
        bins = pd.cut(shown["score"], [-1, 39, 49, 59, 69, 79, 89, 100],
                      labels=["<40", "40s", "50s", "60s", "70s", "80s", "90+"])  # fmt: skip
        st.bar_chart(bins.value_counts().sort_index(), y_label="students", x_label="score %")


def _downloads(exam_id: str) -> None:
    c1, c2, c3 = st.columns(3)
    c1.download_button("Marks (CSV)", exports.marks_csv(exam_id), "marks.csv", "text/csv")
    c2.download_button("Marks + feedback (Excel)", exports.excel_bytes(exam_id), "results.xlsx")
    c3.download_button("Feedback files (zip)", exports.feedback_zip(exam_id), "feedback.zip")


def _flagged(flagged: pd.DataFrame) -> None:
    st.subheader("Answers to check")
    st.caption("These may need a quick check. Marks stay as they are unless you change them.")
    if flagged.empty:
        st.success("Nothing flagged.")
    else:
        st.dataframe(flagged, hide_index=True, width="stretch")


def _one_answer(exam_id: str, rs: list) -> None:
    st.subheader("Look at one answer")
    students = sorted({res.student_of(r.item) for r in rs})
    c1, c2 = st.columns(2)
    student = c1.selectbox("Student", students)
    mine = [r for r in rs if res.student_of(r.item) == student]
    qid = c2.selectbox("Question", [r.item.question_id for r in mine])
    r = next(x for x in mine if x.item.question_id == qid)
    row = next(x for x in report.rows(exam_id, student) if x["question"] == qid)
    changed = f" (model gave {row['model_mark']:g})" if row["overridden"] else ""
    st.markdown(f"**{row['mark']:g} / {row['max']:g}**{changed}")
    original_pages(exam_id, student)
    left, right = st.columns(2)
    left.caption("Student's answer (the text the pipeline marked)")
    with left:
        rich.rich_text(r.item.student_answer)
    right.caption("Feedback to the student")
    with right:
        rich.rich_text(row["feedback"], empty="(none: full marks)")
    _override_form(exam_id, student, row)
    if r.grading:
        for v in r.grading.verdicts:
            quote = f" Quote: “{v.evidence}”" if v.evidence else ""
            head = f"{v.point_id}: {v.status}, {v.marks_awarded:g} mark(s)."
            rich.rich_text(f"{head} {v.reason}{quote}")
    if r.flags:
        st.caption("Flags: " + ", ".join(r.flags))
    with st.expander(f"Full feedback report for {student}"):
        rich.markdown(report.markdown(exam_id, student))


def _override_form(exam_id: str, student: str, row: dict) -> None:
    user = session.current_user()
    with st.expander("Change this mark", expanded=row["overridden"]):
        key = f"ov_{exam_id}_{student}_{row['question']}"
        mark = st.number_input(
            "New mark", 0.0, float(row["max"]), float(row["mark"]), step=0.5, key=f"{key}_m"
        )
        comment = st.text_input(
            "Reason (shown to the student)", value=row["teacher_comment"], key=f"{key}_c"
        )
        a, b = st.columns(2)
        if a.button("Save mark", key=f"{key}_s"):
            grades.override(exam_id, student, row["question"], mark, comment, user["username"])
            st.rerun()
        if row["overridden"] and b.button("Back to the model's mark", key=f"{key}_r"):
            grades.clear_override(exam_id, student, row["question"], user["username"])
            st.rerun()

"""Revision test: does the feedback help? A simulated student rewrites the answer using only the
feedback, and the grader marks the rewrite. A control rewrite with no feedback shows how much
of the gain is just rewording. Leakage shows how much of the model answer the feedback gives away.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.config import PipelineConfig
from autograde.llm import LLMClient
from autograde.pipeline.run import mark_item
from autograde.schemas import Feedback, Grading, Result, RubricRecord
from autograde.textutil import leakage

NO_FEEDBACK = "No feedback was provided."


def answer_digest(answer: str) -> str:
    """Short hash of the student's answer: the no-feedback control depends on the exact text, and
    a noisy copy of an answer keeps its item id."""
    return hashlib.sha1(answer.encode("utf-8")).hexdigest()[:8]


class Revised(BaseModel):
    answer: str


class RevisionRow(BaseModel):
    id: str
    max_mark: float
    before: float
    with_feedback: float
    without_feedback: float
    leak_feedback: float
    leak_revised: float
    revised_answer: str = ""
    control_answer: str = ""
    revised_verdicts: list[dict] = []
    flagged: list[str] = []  # points the feedback said lost marks
    before_marks: dict[str, float] = {}  # marks per point before the rewrite


def feedback_text(fb: Feedback) -> str:
    """The feedback as the student would read it."""
    return fb.text()


def revise(result: Result, feedback: str, student: LLMClient, own_knowledge: bool = False) -> str:
    """The student's rewrite. By default the student may use only the answer and the feedback, so
    the test measures what the feedback hands over; with `own_knowledge` the student may also use
    what they know, so the feedback has to point them to what they can already supply."""
    item = result.item
    user = prompts.render(
        "revise.user", question=item.question, student_answer=item.student_answer, feedback=feedback
    )
    return student.ask(
        prompts.system("revise.own" if own_knowledge else "revise"), user, Revised
    ).answer


def _mark(
    result: Result, answer: str, record: RubricRecord, grader: LLMClient, cfg: PipelineConfig
) -> Grading:
    item = result.item.model_copy(update={"student_answer": answer})
    return mark_item(item, record, grader, cfg)[1]


def revision_test(
    results: Sequence[Result],
    records: Mapping[str, RubricRecord],
    grader: LLMClient,
    student: LLMClient,
    cfg: PipelineConfig,
    control_path: Path,
    workers: int = 4,
    own_knowledge: bool = False,
) -> list[RevisionRow]:
    """Only answers that lost marks are tested: a full-mark answer has nothing to gain.

    The no-feedback rewrite depends only on the answer, so its mark is cached in `control_path`
    and shared by every feedback variant run on the same answers.
    """
    todo = [
        r
        for r in results
        if r.feedback
        and r.grading
        and r.item.student_answer.strip()
        and r.predicted_mark < r.item.max_mark
    ]
    cache: dict[str, dict] = {}
    if control_path.exists():
        cache = json.loads(control_path.read_text(encoding="utf-8"))
    prefix = f"{grader.name}|{student.name}|{'own|' if own_knowledge else ''}"

    def one(r: Result) -> RevisionRow:
        assert r.feedback is not None
        record = records[r.item.question_key]
        text = feedback_text(r.feedback)
        revised = revise(r, text, student, own_knowledge)
        key = prefix + r.item.id + "|" + answer_digest(r.item.student_answer)
        if key not in cache:
            plain = revise(r, NO_FEEDBACK, student, own_knowledge)
            cache[key] = {"answer": plain, "mark": _mark(r, plain, record, grader, cfg).total}
        after = _mark(r, revised, record, grader, cfg)
        return RevisionRow(
            id=r.item.id,
            max_mark=r.item.max_mark,
            before=r.predicted_mark,
            with_feedback=after.total,
            without_feedback=cache[key]["mark"],
            leak_feedback=leakage(text, r.item.model_answer),
            leak_revised=leakage(revised, r.item.model_answer),
            revised_answer=revised,
            control_answer=cache[key]["answer"],
            revised_verdicts=[
                {"point_id": v.point_id, "status": v.status, "marks": v.marks_awarded}
                for v in after.verdicts
            ],
            flagged=[x.point_id for x in r.feedback.improvements],
            before_marks={v.point_id: v.marks_awarded for v in r.grading.verdicts},
        )

    with ThreadPoolExecutor(workers) as pool:
        rows = list(pool.map(one, todo))
    control_path.parent.mkdir(parents=True, exist_ok=True)
    control_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return rows


def _per_point(rows: Sequence[RevisionRow]) -> tuple[float | None, float | None]:
    """Per point, not per total: uptake is the share of points the feedback named that earned
    more marks in the rewrite; harm is the share of the other points that earned less. A total
    reaches its ceiling when the rewrite copies the feedback; these two do not hide a point
    that was fixed while another was broken."""
    named = fixed = other = broken = 0
    for r in rows:
        after = {v["point_id"]: v["marks"] for v in r.revised_verdicts}
        for pid, was in r.before_marks.items():
            now = after.get(pid, was)
            if pid in r.flagged:
                named += 1
                fixed += now > was + 1e-6
            else:
                other += 1
                broken += now < was - 1e-6
    return (
        round(fixed / named, 3) if named else None,
        round(broken / other, 3) if other else None,
    )


def summarise(rows: Sequence[RevisionRow]) -> dict[str, float | int]:
    """Gains are in marks as a share of the question's total, so questions are comparable."""
    n = len(rows)
    if not n:
        return {"n": 0}
    g_with = [(r.with_feedback - r.before) / r.max_mark for r in rows]
    g_without = [(r.without_feedback - r.before) / r.max_mark for r in rows]

    def mean(xs: Sequence[float]) -> float:
        return sum(xs) / len(xs)

    uptake, harm = _per_point(rows)
    return {
        "n": n,
        "uptake": uptake,
        "harm": harm,
        "gain_with_feedback": round(mean(g_with), 4),
        "gain_without_feedback": round(mean(g_without), 4),
        "lift": round(mean(g_with) - mean(g_without), 4),
        "share_improved": round(sum(g > 0.005 for g in g_with) / n, 3),
        "share_worse": round(sum(g < -0.005 for g in g_with) / n, 3),
        "leak_in_feedback": round(mean([r.leak_feedback for r in rows]), 3),
        "leak_in_revised": round(mean([r.leak_revised for r in rows]), 3),
    }

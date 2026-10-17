"""Transfer test: does the feedback teach the idea, or only the answer to this question?

A simulated student reads the feedback on one question, then answers a different question about
the same concept. If the feedback only hands over the answer, the student can fix the original
question (the revision test) but not the new one. Compare the two lifts.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.evaluation.revision import NO_FEEDBACK, feedback_text
from autograde.llm import LLMClient
from autograde.pipeline.baseline import grade_baseline
from autograde.schemas import Item, Result


class TransferQ(BaseModel):
    question: str
    model_answer: str


class Attempt(BaseModel):
    answer: str


class TransferRow(BaseModel):
    id: str
    max_mark: float
    new_question: str
    with_feedback: float
    without_feedback: float
    answer_with: str = ""
    answer_without: str = ""


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def _save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def make_transfer(item: Item, writer: LLMClient) -> TransferQ:
    user = prompts.render(
        "transfer.make.user", question=item.question, model_answer=item.model_answer
    )
    return writer.ask(prompts.system("transfer.make"), user, TransferQ)


def attempt(item: Item, feedback: str, tq: TransferQ, student: LLMClient) -> str:
    user = prompts.render(
        "transfer.attempt.user",
        question=item.question,
        student_answer=item.student_answer,
        feedback=feedback,
        new_question=tq.question,
    )
    return student.ask(prompts.system("transfer.attempt"), user, Attempt).answer


def _mark(item: Item, tq: TransferQ, answer: str, grader: LLMClient) -> float:
    new = item.model_copy(
        update={
            "id": item.id + "~transfer",
            "question_id": item.question_id + "~transfer",
            "question": tq.question,
            "model_answer": tq.model_answer,
            "student_answer": answer,
        }
    )
    return grade_baseline(new, grader).predicted_mark  # one-prompt marking: no scheme to build


def transfer_test(
    results: Sequence[Result],
    grader: LLMClient,
    student: LLMClient,
    writer: LLMClient,
    cache_dir: Path,
    workers: int = 4,
) -> list[TransferRow]:
    """Only answers that lost marks. New questions and no-feedback attempts are cached in
    `cache_dir` so every feedback variant is tested on the same new questions."""
    todo = [
        r
        for r in results
        if r.feedback and r.item.student_answer.strip() and r.predicted_mark < r.item.max_mark
    ]
    qpath, cpath = cache_dir / "transfer_questions.json", cache_dir / "transfer_control.json"
    questions, control = _load(qpath), _load(cpath)
    qkey = writer.name + "|"
    ckey = f"{grader.name}|{student.name}|"

    def one(r: Result) -> TransferRow:
        assert r.feedback is not None
        item = r.item
        if qkey + item.id not in questions:
            questions[qkey + item.id] = make_transfer(item, writer).model_dump()
        tq = TransferQ.model_validate(questions[qkey + item.id])
        if ckey + item.id not in control:
            plain = attempt(item, NO_FEEDBACK, tq, student)
            control[ckey + item.id] = {"answer": plain, "mark": _mark(item, tq, plain, grader)}
        guided = attempt(item, feedback_text(r.feedback), tq, student)
        return TransferRow(
            id=item.id,
            max_mark=item.max_mark,
            new_question=tq.question,
            with_feedback=_mark(item, tq, guided, grader),
            without_feedback=control[ckey + item.id]["mark"],
            answer_with=guided,
            answer_without=control[ckey + item.id]["answer"],
        )

    with ThreadPoolExecutor(workers) as pool:
        rows = list(pool.map(one, todo))
    _save(qpath, questions)
    _save(cpath, control)
    return rows


def summarise(rows: Sequence[TransferRow]) -> dict:
    """Marks as a share of the total, so questions are comparable."""
    if not rows:
        return {"n": 0}
    with_ = [r.with_feedback / r.max_mark for r in rows]
    without = [r.without_feedback / r.max_mark for r in rows]

    def mean(xs: Sequence[float]) -> float:
        return sum(xs) / len(xs)

    return {
        "n": len(rows),
        "transfer_with_feedback": round(mean(with_), 4),
        "transfer_without_feedback": round(mean(without), 4),
        "transfer_lift": round(mean(with_) - mean(without), 4),
    }

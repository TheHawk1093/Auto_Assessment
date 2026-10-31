"""Reads a finished run (the model's output, before any teacher override)."""

from __future__ import annotations

import json

import pandas as pd

from app.services.storage import run_path
from autograde.intake.exam import student_of
from autograde.pipeline.review import LABELS, review_reasons
from autograde.pipeline.run import read_results
from autograde.schemas import Result

__all__ = ["student_of"]


def has_results(exam_id: str) -> bool:
    return (run_path(exam_id) / "marks.csv").exists()


def intake(exam_id: str) -> dict:
    path = run_path(exam_id) / "intake.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def schemes_text(exam_id: str) -> str:
    path = run_path(exam_id) / "schemes.md"
    return path.read_text(encoding="utf-8") if path.exists() else ""


def results(exam_id: str) -> list[Result]:
    path = run_path(exam_id) / "results.jsonl"
    return read_results(path) if path.exists() else []


def progress(exam_id: str) -> tuple[int, int]:
    """(answers marked so far, answers to mark). The second is 0 until intake has run."""
    info = intake(exam_id)
    total = len(info.get("paper", {}).get("questions", [])) * len(info.get("students", []))
    path = run_path(exam_id) / "results.jsonl"
    done = sum(1 for _ in path.open(encoding="utf-8")) if path.exists() else 0
    return done, total


def flagged_table(rs: list[Result]) -> pd.DataFrame:
    rows = []
    for r in rs:
        reasons = review_reasons(r)
        if reasons:
            rows.append(
                {
                    "student": student_of(r.item),
                    "question": r.item.question_id,
                    "mark": f"{r.predicted_mark:g} / {r.item.max_mark:g}",
                    "why look": "; ".join(LABELS[x] for x in reasons),
                }
            )
    return pd.DataFrame(rows, columns=["student", "question", "mark", "why look"])

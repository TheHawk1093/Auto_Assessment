"""Build a single self-contained HTML page to read a finished run: question, model answer,
student answer, teacher mark vs ours, marking points with quotes, and the feedback."""

from __future__ import annotations

import json
import random
from collections import defaultdict
from collections.abc import Sequence
from importlib import resources
from pathlib import Path

from autograde.evaluation.metrics import report
from autograde.pipeline.rubric import cached_record
from autograde.pipeline.verify import evidence_in_answer
from autograde.schemas import Result

PLACEHOLDER = "__DATA__"


def _safe_json(obj: object) -> str:
    """JSON that is safe inside a <script> tag."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")


def sample_spread(results: Sequence[Result], n: int, seed: int = 0) -> list[Result]:
    """Pick n results spread over as many different questions as possible (round-robin)."""
    by_question: dict[str, list[Result]] = defaultdict(list)
    for r in sorted(results, key=lambda r: r.item.id):  # same pick whatever the run order
        by_question[r.item.question_key].append(r)
    rng = random.Random(seed)
    queues = list(by_question.values())
    rng.shuffle(queues)
    for q in queues:
        rng.shuffle(q)
    picked: list[Result] = []
    while len(picked) < n and any(queues):
        for q in queues:
            if q and len(picked) < n:
                picked.append(q.pop())
    return picked


def sample_by_mark(results: Sequence[Result], n: int) -> list[Result]:
    """Pick n results evenly along the teacher's marks (low to high), one per question where
    possible, so a small sample shows weak, middling and strong answers."""
    ranked = sorted(results, key=lambda r: (r.item.human_mark / r.item.max_mark, r.item.id))
    picked: list[Result] = []
    seen: set[str] = set()
    for k in range(n):
        centre = round(k * (len(ranked) - 1) / max(n - 1, 1))
        order = sorted(range(len(ranked)), key=lambda i: abs(i - centre))
        for i in order:
            r = ranked[i]
            if r.item.id not in {x.item.id for x in picked} and r.item.question_key not in seen:
                picked.append(r)
                seen.add(r.item.question_key)
                break
    return picked


def _grading_with_checks(r: Result) -> dict | None:
    """Grading as a dict, with a flag per verdict saying whether its quote is in the answer."""
    if not r.grading:
        return None
    out = r.grading.model_dump()
    for v in out["verdicts"]:
        v["evidence_ok"] = bool(v["evidence"]) and evidence_in_answer(
            v["evidence"], r.item.student_answer
        )
    return out


def build_data(
    results: Sequence[Result],
    title: str,
    rubrics_dir: Path,
    client_name: str,
    judgements: dict[str, dict] | None = None,
    run_info: dict | None = None,
) -> dict:
    """The JSON the page renders: one entry per answer, with the scheme text attached."""
    judgements = judgements or {}
    items = []
    for r in results:
        record = cached_record(rubrics_dir, client_name, r.item.question_key)
        points = (
            {p.id: {"description": p.description, "marks": p.marks} for p in record.rubric.points}
            if record
            else {}
        )
        items.append(
            {
                "item": r.item.model_dump(),
                "mode": r.mode,
                "predicted": r.predicted_mark,
                "reading": r.reading.model_dump() if r.reading else None,
                "grading": _grading_with_checks(r),
                "feedback": r.feedback.model_dump() if r.feedback else None,
                "flags": r.flags,
                "points": points,
                "scheme_ok": record.selftest_passed if record else None,
                "scheme_notes": record.selftest_notes if record else [],
                "judgement": judgements.get(r.item.id),
            }
        )
    return {"title": title, "metrics": report(results), "items": items, "run": run_info or {}}


def render_html(data: dict) -> str:
    template = resources.files(__package__).joinpath("report.html").read_text(encoding="utf-8")
    return template.replace(PLACEHOLDER, _safe_json(data))


def write_report(
    results: Sequence[Result],
    out_path: Path,
    title: str,
    rubrics_dir: Path,
    client_name: str,
    judgements: dict[str, dict] | None = None,
    run_info: dict | None = None,
) -> Path:
    data = build_data(results, title, rubrics_dir, client_name, judgements, run_info)
    out_path.write_text(render_html(data), encoding="utf-8")
    return out_path

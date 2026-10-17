"""One page, one tab per method, the same few answers in every tab.

Each tab shows, for the same questions: the model answer, the student answer, the teacher's
mark, how that method marked it and what feedback it wrote, and (where it was tested) whether
a student could use the feedback to improve the answer. The page is a single file with the data
embedded, so it opens offline (maths rendering needs the KaTeX files from the internet).
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from importlib import resources
from pathlib import Path

from autograde.pipeline.rubric import cached_record
from autograde.schemas import Result
from autograde.viewer.build import _grading_with_checks, sample_by_mark

PLACEHOLDER = "/*__DATA__*/null"


@dataclass(frozen=True)
class Tab:
    run: str  # folder name under runs/
    label: str
    short: str  # one line under the tab name
    desc: str  # what this method is, in plain words


def _read_json(path: Path) -> dict | list | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _read_lines(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def _stats(run_dir: Path) -> dict:
    metrics = _read_json(run_dir / "metrics.json") or {}
    overall = metrics.get("overall", {}) if isinstance(metrics, dict) else {}
    usage = _read_json(run_dir / "usage.json") or {}
    return {
        "error": overall.get("mean_abs_error"),
        "bias": overall.get("bias"),
        "pearson": overall.get("pearson"),
        "qwk": overall.get("qwk"),
        "n": overall.get("n"),
        "cost": usage.get("cost_usd") if isinstance(usage, dict) else None,
    }


def _client_name(setup: dict) -> str:
    llm = setup.get("llm", {})
    name = f"{llm.get('backend', 'claude_cli')}-{llm.get('model', 'sonnet')}"
    return name + (f"-{llm['effort']}" if llm.get("effort") else "")


def method_data(tab: Tab, runs_dir: Path, cache_dir: Path, ids: Sequence[str]) -> dict:
    run_dir = runs_dir / tab.run
    setup = _read_json(run_dir / "run.json") or {}
    variant = setup.get("pipeline", {}).get("rubric_variant", "generated")
    client = _client_name(setup)
    results = {}
    for line in _read_lines(run_dir / "results.jsonl"):
        r = Result.model_validate(line)
        results[r.item.id] = r
    revision = {}
    transfer = {}
    for name in ("revision_rows.jsonl", "revision_rows_sample.jsonl"):  # sample wins if both
        revision.update({x["id"]: x for x in _read_lines(run_dir / name)})
    for name in ("transfer_rows.jsonl", "transfer_rows_sample.jsonl"):
        transfer.update({x["id"]: x for x in _read_lines(run_dir / name)})
    judged = {x["id"]: x for x in _read_lines(run_dir / "feedback_judgements.jsonl")}

    answers: dict[str, dict] = {}
    for id_ in ids:
        r = results.get(id_)
        if r is None:
            continue
        record = cached_record(cache_dir, client, r.item.question_key, variant)
        points = (
            {p.id: {"description": p.description, "marks": p.marks} for p in record.rubric.points}
            if record
            else {}
        )
        grading = _grading_with_checks(r)
        verdicts = (
            [
                {
                    "point_id": v["point_id"],
                    "status": v["status"],
                    "marks": v["marks_awarded"],
                    "evidence": v["evidence"],
                    "evidence_ok": v["evidence_ok"],
                    "reason": v["reason"],
                }
                for v in grading["verdicts"]
            ]
            if grading
            else None
        )
        rev = revision.get(id_)
        judgement = judged.get(id_)
        answers[id_] = {
            "predicted": r.predicted_mark,
            "reading": r.reading.model_dump() if r.reading else None,
            "verdicts": verdicts,
            "points": points,
            "feedback": r.feedback.model_dump() if r.feedback else None,
            "revision": rev,
            "transfer": transfer.get(id_),
            "judgement": {k: v for k, v in judged[id_].items() if k not in ("id", "note")}
            if judgement
            else None,
        }
    return {
        "label": tab.label,
        "short": tab.short,
        "desc": tab.desc,
        "stats": _stats(run_dir),
        "answers": answers,
    }


def build_data(
    tabs: Sequence[Tab], runs_dir: Path, cache_dir: Path, n: int, title: str, subtitle: str
) -> dict:
    first = [
        Result.model_validate(x) for x in _read_lines(runs_dir / tabs[0].run / "results.jsonl")
    ]
    chosen = sample_by_mark(first, n)  # depends only on the items, so every run shows the same
    ids = [r.item.id for r in chosen]
    questions = [
        {
            "id": r.item.id,
            "question": r.item.question,
            "model_answer": r.item.model_answer,
            "student_answer": r.item.student_answer,
            "max_mark": r.item.max_mark,
            "human_mark": r.item.human_mark,
            "human_feedback": r.item.human_feedback,
        }
        for r in chosen
    ]
    methods = [method_data(t, runs_dir, cache_dir, ids) for t in tabs]
    return {"title": title, "subtitle": subtitle, "questions": questions, "methods": methods}


def write_compare(data: dict, out_path: Path) -> Path:
    template = resources.files(__package__).joinpath("compare.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template.replace(PLACEHOLDER, payload), encoding="utf-8")
    return out_path

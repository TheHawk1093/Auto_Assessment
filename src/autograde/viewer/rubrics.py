"""A page to read the rubrics, one dataset at a time, at each strictness level.

Shows how each dataset's teacher marks (the policy), every question's lenient, moderate and
harsh rubric side by side, and, where the same answers were marked under each rubric, how the
marks and the feedback changed with the rubric.
"""

from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

from autograde.datasets.loaders import load_dataset
from autograde.evaluation.compliance import compliance
from autograde.pipeline.levels import LEVELS, dataset_policy
from autograde.pipeline.rubric import cached_record
from autograde.schemas import Result

PLACEHOLDER = "/*__DATA__*/null"
NAMES = {"digiklausur": "DigiKlausur", "saf": "SAF", "mohler": "Mohler", "engsaf": "EngSAF"}
RUN_PREFIX = {
    "digiklausur": "dk_lv_",
    "saf": "saf_lv_",
    "mohler": "mohler_lv_",
    "engsaf": "engsaf_lv_",
}


def _results(path: Path) -> dict[str, Result]:
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    return {r.item.id: r for r in (Result.model_validate_json(x) for x in lines if x.strip())}


def _rubric_view(record) -> dict | None:
    if record is None:
        return None
    r = record.rubric
    return {
        "notes": r.notes,
        "points": [
            {
                "id": p.id,
                "description": p.description,
                "marks": p.marks,
                "partial": p.partial_credit,
            }
            for p in r.points
        ],
    }


def dataset_data(
    name: str, data_dir: Path, cache_dir: Path, runs_dir: Path, client_name: str
) -> dict:
    items = load_dataset(name, data_dir)
    first = {}
    count: dict[str, int] = {}
    for it in items:
        first.setdefault(it.question_key, it)
        count[it.question_key] = count.get(it.question_key, 0) + 1
    runs = {lv: _results(runs_dir / f"{RUN_PREFIX[name]}{lv}" / "results.jsonl") for lv in LEVELS}
    graded: dict[str, list[dict]] = {}
    ids = set.intersection(*(set(r) for r in runs.values())) if all(runs.values()) else set()
    for id_ in sorted(ids):
        base = runs["moderate"][id_]
        entry = {
            "student_answer": base.item.student_answer,
            "human_mark": base.item.human_mark,
            "levels": {
                lv: {
                    "predicted": runs[lv][id_].predicted_mark,
                    "feedback": runs[lv][id_].feedback.model_dump()
                    if runs[lv][id_].feedback
                    else None,
                    "status": [
                        [v.point_id, v.status]
                        for v in (runs[lv][id_].grading.verdicts if runs[lv][id_].grading else [])
                    ],
                }
                for lv in LEVELS
            },
        }
        graded.setdefault(base.item.question_key, []).append(entry)
    questions = []
    for key in sorted(first):
        it = first[key]
        levels = {lv: _rubric_view(cached_record(cache_dir, client_name, key, lv)) for lv in LEVELS}
        questions.append(
            {
                "key": key,
                "question": it.question,
                "model_answer": it.model_answer,
                "max_mark": it.max_mark,
                "n_answers": count[key],
                "levels": levels,
                "graded": graded.get(key, []),
            }
        )
    return {
        "name": NAMES.get(name, name),
        "policy": dataset_policy(name),
        "max_mark": next(iter(first.values())).max_mark,
        "compliance": compliance({lv: list(r.values()) for lv, r in runs.items() if r})
        if ids
        else None,
        "questions": questions,
    }


def build_data(data_dir: Path, cache_dir: Path, runs_dir: Path, client_name: str, datasets) -> dict:
    return {
        "title": "Rubrics at three strictness levels",
        "sets": [dataset_data(d, data_dir, cache_dir, runs_dir, client_name) for d in datasets],
    }


def write_page(data: dict, out_path: Path) -> Path:
    template = resources.files(__package__).joinpath("rubrics.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template.replace(PLACEHOLDER, payload), encoding="utf-8")
    return out_path

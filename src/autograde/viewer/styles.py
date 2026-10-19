"""A page to compare feedback styles on the same answers, with measured stats beside the text.

Every style is run on the same marks (`autograde refeedback`), so only the feedback differs. The
page shows how long and how structured each style is, how it was scored by the judge and by
the rewrite and transfer tests, and lets the reader rate styles and choose one.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from importlib import resources
from pathlib import Path

from autograde.evaluation.revision import feedback_text
from autograde.schemas import Result
from autograde.textutil import leakage
from autograde.viewer.build import sample_by_mark

PLACEHOLDER = "/*__DATA__*/null"

STYLES = {
    "brief": ("Brief", "One gap only, under 45 words"),
    "coach": ("Coach", "Warm and encouraging, short"),
    "standard": ("Standard", "Plain: what is missing, why it matters, what to try"),
    "hints": ("Hints", "Guides with questions and does not state the missing idea"),
    "formal": ("Formal", "An examiner's report register"),
    "critique": ("Critique", "Standard feedback that a second pass reviewed and tightened"),
    "best3": ("Best of 3", "Three drafts, code checks, then the best is picked"),
    "detailed": ("Detailed", "Thorough, with a worked correction, 150 to 300 words"),
}


def _read_results(path: Path) -> dict[str, Result]:
    if not path.exists():
        return {}
    lines = path.read_text(encoding="utf-8").splitlines()
    return {r.item.id: r for r in (Result.model_validate_json(x) for x in lines if x.strip())}


def _json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _words(r: Result) -> int:
    return len(feedback_text(r.feedback).split()) if r.feedback else 0


def style_stats(run_dir: Path, results: Sequence[Result]) -> dict:
    fbs = [r for r in results if r.feedback]
    imps = [x for r in fbs for x in r.feedback.improvements]  # type: ignore[union-attr]
    n = max(1, len(fbs))
    judge = _json(run_dir / "feedback_scores.json").get("pass_rates", {})
    revision = _json(run_dir / "revision_scores.json")
    transfer = _json(run_dir / "transfer_scores.json")
    return {
        "words": round(sum(_words(r) for r in fbs) / n, 1),
        "items": round(sum(len(r.feedback.improvements) for r in fbs) / n, 2),  # type: ignore[union-attr]
        "with_why": round(sum(bool(x.why.strip()) for x in imps) / max(1, len(imps)), 2),
        "leak": round(
            sum(leakage(feedback_text(r.feedback), r.item.model_answer) for r in fbs) / n,
            3,  # type: ignore[arg-type]
        ),
        "judge": judge,
        "revision_lift": revision.get("lift"),
        "transfer_lift": transfer.get("transfer_lift"),
    }


def build_data(runs_dir: Path, n_answers: int = 6) -> dict:
    sets = [("DigiKlausur", "dk_s0_fb_", "neural networks"), ("SAF", "saf_s0_fb_", "networking")]
    out = []
    for label, prefix, topic in sets:
        per_style = {}
        for key in STYLES:
            run = runs_dir / f"{prefix}{key}"
            res = _read_results(run / "results.jsonl")
            if res:
                per_style[key] = (run, res)
        if "standard" not in per_style:
            continue
        base = list(per_style["standard"][1].values())
        chosen = sample_by_mark(base, n_answers)
        answers = []
        for r in chosen:
            it = r.item
            answers.append(
                {
                    "id": it.id,
                    "question": it.question,
                    "model_answer": it.model_answer,
                    "student_answer": it.student_answer,
                    "max_mark": it.max_mark,
                    "human_mark": it.human_mark,
                    "human_feedback": it.human_feedback,
                    "predicted": r.predicted_mark,
                    "feedback": {
                        k: (
                            v[1][it.id].feedback.model_dump()
                            if it.id in v[1] and v[1][it.id].feedback
                            else None
                        )
                        for k, v in per_style.items()
                    },
                }
            )
        styles = [
            {
                "key": k,
                "label": STYLES[k][0],
                "desc": STYLES[k][1],
                "stats": style_stats(run, list(res.values())),
            }
            for k, (run, res) in per_style.items()
        ]
        styles.sort(key=lambda s: s["stats"]["words"])  # shortest first: a granularity ladder
        out.append({"label": label, "topic": topic, "styles": styles, "answers": answers})
    return {"title": "Feedback styles on the same answers", "sets": out}


def write_page(data: dict, out_path: Path) -> Path:
    template = resources.files(__package__).joinpath("styles.html").read_text(encoding="utf-8")
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(template.replace(PLACEHOLDER, payload), encoding="utf-8")
    return out_path

"""Marking in an Indic language: grade the answers as written (native) and after translation to
English, against the dataset's human labels (correct / incorrect).

    python tools/ocr/indic_grading_eval.py --dataset scaa_hindi --n 40 --mode baseline \
        --out runs/scaa_hi_baseline

Both views use the same model, items and settings; only the language differs. The translation is
done by the same model, so no other service is needed. The sample is balanced between correct
and incorrect answers, from the dev split (questions are split by hash; the other questions are
never touched). Agreement is reported as accuracy, Cohen's kappa and the recall of each class.
"""

from __future__ import annotations

import argparse
import json
import logging
import random
import sys
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.config import load_settings
from autograde.datasets import load_dataset, split_of
from autograde.llm import build_client
from autograde.pipeline.run import run_items
from autograde.schemas import Item

ROOT = Path(__file__).resolve().parents[2]
log = logging.getLogger("indic_grading_eval")


class Translated(BaseModel):
    question: str
    model_answer: str
    student_answer: str


def sample(items: list[Item], n: int, seed: int) -> list[Item]:
    """n dev answers, half correct and half incorrect."""
    dev = [i for i in items if split_of(i.question_key) == "dev"]
    rng = random.Random(seed)
    right = [i for i in dev if i.human_mark == 1.0]
    wrong = [i for i in dev if i.human_mark == 0.0]
    return rng.sample(right, n // 2) + rng.sample(wrong, n - n // 2)


def translate(items: list[Item], client, cache_path: Path) -> list[Item]:
    cache = json.loads(cache_path.read_text("utf-8")) if cache_path.exists() else {}
    out = []
    for it in items:
        if it.id not in cache:
            user = (
                f"Question:\n{it.question}\n\nModel answer:\n{it.model_answer}\n\n"
                f"Student answer:\n{it.student_answer}"
            )
            cache[it.id] = client.ask(prompts.system("translate"), user, Translated).model_dump()
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), "utf-8")
        t = cache[it.id]
        out.append(
            it.model_copy(
                update={
                    "question": t["question"],
                    "model_answer": t["model_answer"],
                    "student_answer": t["student_answer"],
                }
            )
        )
    return out


def agreement(results) -> dict:
    truth = [r.item.human_mark >= 0.5 for r in results]
    pred = [r.predicted_mark / r.item.max_mark >= 0.5 for r in results]
    n = len(results)
    tp = sum(t and p for t, p in zip(truth, pred, strict=True))
    tn = sum((not t) and (not p) for t, p in zip(truth, pred, strict=True))
    pos, neg = sum(truth), n - sum(truth)
    acc = (tp + tn) / n
    chance = (pos * sum(pred) + neg * (n - sum(pred))) / (n * n)
    return {
        "n": n,
        "accuracy": round(acc, 3),
        "kappa": round((acc - chance) / (1 - chance), 3) if chance < 1 else 0.0,
        "recall_correct": round(tp / pos, 3) if pos else None,
        "recall_incorrect": round(tn / neg, 3) if neg else None,
    }


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser()
    p.add_argument("--dataset", default="scaa_hindi")
    p.add_argument("--n", type=int, default=40)
    p.add_argument("--seed", type=int, default=1)
    p.add_argument("--mode", choices=["baseline", "pipeline"], default="baseline")
    p.add_argument("--views", default="native,english")
    p.add_argument("--config", default=str(ROOT / "configs/experiments/indic/indic_gemini.yaml"))
    p.add_argument("--out", required=True)
    a = p.parse_args()
    logging.basicConfig(level=logging.WARNING)

    settings = load_settings(Path(a.config))
    out = ROOT / a.out
    settings.paths.rubrics_dir = out / "rubrics"
    client = build_client(settings.llm)
    items = sample(load_dataset(a.dataset, ROOT / "data/raw"), a.n, a.seed)
    summary = {}
    for view in a.views.split(","):
        if view == "english":
            settings.pipeline.feedback_language = ""  # feedback for the English view is English
            work = translate(items, client, out / "translations.json")
        else:
            work = items
        res = run_items(work, a.mode, client, settings, out / f"{view}.jsonl")
        summary[view] = agreement(res)
        summary[view]["with_feedback"] = sum(r.feedback is not None for r in res)
        print(view, json.dumps(summary[view]))
    summary["usage"] = client.usage.as_dict()
    (out / "summary.json").write_text(json.dumps(summary, indent=1), "utf-8")
    print("usage:", json.dumps(summary["usage"]))


if __name__ == "__main__":
    main()

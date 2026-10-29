"""Robustness test: do marks stay put when the answer is written differently but says the same?

Each perturbation rewrites finished answers without changing what they say (or, for the "drop"
group, by removing half of it), the answers are marked again with the same scheme, and the shift
from the original mark is reported. Two controls give the scale: re-marking the unchanged answer
shows the marker's own noise, and the "drop" group must lower the mark or the test is not
sensitive.

Two kinds of perturbation:
- code: spelling slips, case and punctuation, shuffled sentences, shouting, text-speak, filler,
  an irrelevant sentence, the question repeated, half the answer cut off. No model call.
- model: a model rewrites the answer as a paraphrase, with synonyms, as a non-native writer,
  informally, or wordily. Cached, so each rewrite is made once.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import re
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.config import PipelineConfig
from autograde.llm import LLMClient
from autograde.pipeline.run import mark_item
from autograde.schemas import Item, Result, RubricRecord

MOVED = 0.1  # a shift of this share of the total or more counts as the mark having moved
DROPPED = 0.05  # a "drop" perturbation must lower the mark by at least this share
_WORD = re.compile(r"(\s+)")
_SENTENCE = re.compile(r"(?<=[.!?।])\s+")


@dataclass(frozen=True)
class Perturbation:
    name: str
    kind: str  # "keep": the mark should not move; "drop": it should go down; "control"
    apply: Callable[[Item, random.Random], str]
    english_only: bool = False


def _is_english(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    return bool(letters) and sum(c.isascii() for c in letters) / len(letters) > 0.95


def spelling(item: Item, rng: random.Random) -> str:
    """About one word in five gets a slip: two letters swapped, one dropped or one doubled."""
    parts = _WORD.split(item.student_answer)
    for i, w in enumerate(parts):
        if len(w) >= 4 and w.isalpha() and rng.random() < 0.2:
            k = rng.randrange(1, len(w) - 1)
            op = rng.choice(("swap", "drop", "double"))
            parts[i] = (
                w[:k] + w[k + 1] + w[k] + w[k + 2 :]
                if op == "swap"
                else w[:k] + w[k + 1 :]
                if op == "drop"
                else w[: k + 1] + w[k:]
            )
    return "".join(parts)


def case_and_punctuation(item: Item, rng: random.Random) -> str:
    text = item.student_answer.lower()
    text = re.sub(r"[,;:!?\"'()]", "", text)
    return re.sub(r"\.(?=\s|$)", "", text)


def shout(item: Item, rng: random.Random) -> str:
    return item.student_answer.upper()


def shuffled_sentences(item: Item, rng: random.Random) -> str:
    sentences = _SENTENCE.split(item.student_answer.strip())
    rng.shuffle(sentences)
    return " ".join(sentences)


_TEXT_SPEAK = {"you": "u", "are": "r", "to": "2", "for": "4", "and": "n", "because": "bcoz"}


def text_speak(item: Item, rng: random.Random) -> str:
    return " ".join(_TEXT_SPEAK.get(w.lower(), w) for w in item.student_answer.split())


def filler(item: Item, rng: random.Random) -> str:
    return f"I think that, basically, {item.student_answer.strip()} That is what I know about this."


def irrelevant_sentence(item: Item, rng: random.Random) -> str:
    return f"{item.student_answer.strip()} The weather today was pleasant and the hall was quiet."


def question_repeated(item: Item, rng: random.Random) -> str:
    return f"{item.question.strip()} {item.student_answer.strip()}"


def half_the_answer(item: Item, rng: random.Random) -> str:
    words = item.student_answer.split()
    return " ".join(words[: max(1, math.ceil(len(words) / 2))])


CODE_PERTURBATIONS = (
    Perturbation("spelling", "keep", spelling),
    Perturbation("case_punctuation", "keep", case_and_punctuation),
    Perturbation("shouting", "keep", shout),
    Perturbation("shuffled_sentences", "keep", shuffled_sentences),
    Perturbation("text_speak", "keep", text_speak, english_only=True),
    Perturbation("filler", "keep", filler, english_only=True),
    Perturbation("irrelevant_sentence", "keep", irrelevant_sentence, english_only=True),
    Perturbation("question_repeated", "keep", question_repeated),
    Perturbation("half_the_answer", "drop", half_the_answer),
)
MODEL_STYLES = ("paraphrase", "synonyms", "nonnative", "informal", "wordy")
NAMES = ("control", *(p.name for p in CODE_PERTURBATIONS), *MODEL_STYLES)


class Rewritten(BaseModel):
    answer: str


def rewrite(item: Item, style: str, writer: LLMClient, cache: dict[str, str]) -> str:
    """The answer rewritten in `style` by a model, once per (style, answer)."""
    key = f"{writer.name}|{style}|{hashlib.sha1(item.student_answer.encode()).hexdigest()[:12]}"
    if key not in cache:
        user = prompts.render("robust.perturb.user", style=style, answer=item.student_answer)
        cache[key] = writer.ask(prompts.system("robust.perturb"), user, Rewritten).answer
    return cache[key]


@dataclass
class Shift:
    perturbation: str
    id: str
    max_mark: float
    before: float
    after: float

    @property
    def share(self) -> float:
        return (self.after - self.before) / self.max_mark


def perturbed(
    item: Item, name: str, rng: random.Random, writer: LLMClient, cache: dict[str, str]
) -> str | None:
    """The perturbed answer, or None when this perturbation does not apply to the item."""
    if name == "control":
        return item.student_answer
    if name in MODEL_STYLES:
        return rewrite(item, name, writer, cache)
    p = next(p for p in CODE_PERTURBATIONS if p.name == name)
    if p.english_only and not _is_english(item.student_answer):
        return None
    if p.kind == "drop" and len(item.student_answer.split()) < 8:
        return None
    if name == "shuffled_sentences" and len(_SENTENCE.split(item.student_answer.strip())) < 2:
        return None
    return p.apply(item, rng)


def robustness_test(
    results: Sequence[Result],
    records: Mapping[str, RubricRecord],
    grader: LLMClient,
    writer: LLMClient,
    cfg: PipelineConfig,
    names: Sequence[str],
    cache_path: Path,
    seed: int = 0,
    workers: int = 4,
) -> list[Shift]:
    """Re-mark each answer under each perturbation. Answers that earned nothing are skipped for
    the "drop" group (there is nothing to lose)."""
    cache: dict[str, str] = (
        json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    )
    jobs = [(n, r) for n in names for r in results if r.item.student_answer.strip()]

    def one(job: tuple[str, Result]) -> Shift | None:
        name, r = job
        rng = random.Random(f"{seed}|{name}|{r.item.id}")
        text = perturbed(r.item, name, rng, writer, cache)
        if text is None:
            return None
        if name == "half_the_answer" and r.predicted_mark <= 0:
            return None
        item = r.item.model_copy(update={"student_answer": text})
        after = mark_item(item, records[r.item.question_key], grader, cfg)[1].total
        return Shift(name, r.item.id, r.item.max_mark, r.predicted_mark, after)

    with ThreadPoolExecutor(workers) as pool:
        shifts = [s for s in pool.map(one, jobs) if s is not None]
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return shifts


def summarise(shifts: Sequence[Shift]) -> dict[str, dict]:
    """Per perturbation: how many answers, the average size of the shift, the average signed
    shift (below zero: marks went down), and the share of answers whose mark moved by MOVED or
    more. For "drop" perturbations, also the share whose mark went down by DROPPED or more."""
    out: dict[str, dict] = {}
    for name in dict.fromkeys(s.perturbation for s in shifts):
        mine = [s.share for s in shifts if s.perturbation == name]
        row = {
            "n": len(mine),
            "mean_abs_shift": round(sum(abs(x) for x in mine) / len(mine), 4),
            "mean_shift": round(sum(mine) / len(mine), 4),
            "moved": round(sum(abs(x) >= MOVED for x in mine) / len(mine), 3),
            "went_down": round(sum(x <= -DROPPED for x in mine) / len(mine), 3),
            "went_up": round(sum(x >= DROPPED for x in mine) / len(mine), 3),
        }
        out[name] = row
    return out

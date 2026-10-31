"""Change the model answer on purpose, to see how much the grader leans on its exact wording.

A grader that knows the subject should give about the same marks when the model answer is
shortened or has words blanked out. A large swing means the marks follow the wording of the
reference, not the idea. The perturbed items get their own question id, so marking schemes are
built afresh from the changed model answer.
"""

from __future__ import annotations

import math
import random
import re
from collections.abc import Sequence

from autograde.schemas import Item
from autograde.textutil import STOP


def mask_words(text: str, frac: float, seed: int = 0) -> str:
    """Blank out about `frac` of the content words (longer than 3 letters, not stop words)."""
    rng = random.Random(seed)
    tokens = re.findall(r"\s+|[^\s]+", text)
    idx = [
        i
        for i, t in enumerate(tokens)
        if re.fullmatch(r"[A-Za-z][A-Za-z-]{3,}", t) and t.lower() not in STOP
    ]
    for i in rng.sample(idx, k=round(len(idx) * frac)):
        tokens[i] = "____"
    return "".join(tokens)


def shorten(text: str, frac: float) -> str:
    """Keep the first `frac` of the sentences, at least one."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    keep = max(1, math.ceil(len(sentences) * frac))
    return " ".join(sentences[:keep])


def parse(spec: str) -> tuple[str, float]:
    """'mask30' -> ('mask', 0.3); 'short50' -> ('short', 0.5)."""
    m = re.fullmatch(r"(mask|short)(\d{1,2})", spec)
    if not m:
        raise ValueError(f"Unknown perturbation {spec!r}. Use mask<percent> or short<percent>.")
    return m.group(1), int(m.group(2)) / 100


def perturb_items(items: Sequence[Item], spec: str, seed: int = 0) -> list[Item]:
    """Return copies of the items with their student answers degraded as `spec` says.

    Args:
        items: Items to copy.
        spec: Kind and fraction, in the form `parse` reads.
        seed: Seed for the random choices.

    """
    kind, frac = parse(spec)
    out = []
    for item in items:
        text = (
            mask_words(item.model_answer, frac, seed)
            if kind == "mask"
            else shorten(item.model_answer, frac)
        )
        out.append(
            item.model_copy(
                update={"model_answer": text, "question_id": f"{item.question_id}~{spec}"}
            )
        )
    return out

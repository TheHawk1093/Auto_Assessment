"""Small text helpers shared by the pipeline and the evaluation code."""

from __future__ import annotations

import re
import unicodedata


def words(text: str) -> list[str]:
    """Split text into lower-cased words in any script.

    A word is a run of letters, combining marks and digits, so Devanagari, Tamil, Bengali and
    the like keep their vowel signs; punctuation (including the danda) separates words, as does
    space.
    """
    out = []
    for token in re.split(r"[\s/-]+", unicodedata.normalize("NFKC", text).lower()):
        word = "".join(c for c in token if unicodedata.category(c)[0] in "LMN")
        if word:
            out.append(word)
    return out


def leakage(text: str, model_answer: str, n: int = 4) -> float:
    """Share of the model answer's n-word phrases that also appear in `text`.

    This catches copied wording only. A paraphrase of the model answer scores low.
    """
    ref = words(model_answer)
    n = max(1, min(n, len(ref)))
    grams = {tuple(ref[i : i + n]) for i in range(len(ref) - n + 1)}
    if not grams:
        return 0.0
    have = words(text)
    seen = {tuple(have[i : i + n]) for i in range(len(have) - n + 1)}
    return len(grams & seen) / len(grams)


STOP = frozenset(
    (
        "the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "was", "were", "be", "been",
        "it", "its", "that", "this", "for", "on", "with", "as", "by", "at", "from", "which", "what",
        "how", "can", "will", "not", "use", "used", "using", "also", "has", "have", "had", "their",
        "there", "than", "then", "they",
    )
)  # fmt: skip

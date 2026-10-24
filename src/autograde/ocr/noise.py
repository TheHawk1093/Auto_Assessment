"""Simulated handwriting-OCR noise for typed answers, seeded so runs are repeatable.

Real OCR of handwriting confuses look-alike letters, glues or splits words, drops
punctuation and loses sub/superscripts. Each level applies these errors at a higher rate.
Only the student answer is changed; question and model answer stay clean.
"""

from __future__ import annotations

import random
import re
from collections.abc import Sequence

from autograde.schemas import Item

# per-level rates: char confusion, split word, merge words, drop punctuation,
# drop short word, stray character, hyphenate at a line break, lose math symbols
LEVELS: dict[str, dict[str, float]] = {
    "light": dict(conf=0.015, split=0.01, merge=0.01, punct=0.10, drop=0.01, stray=0.005,
                  hyph=0.02, math=0.5),
    "medium": dict(conf=0.05, split=0.03, merge=0.04, punct=0.30, drop=0.03, stray=0.015,
                   hyph=0.05, math=0.8),
    "heavy": dict(conf=0.12, split=0.07, merge=0.09, punct=0.55, drop=0.07, stray=0.04,
                  hyph=0.10, math=1.0),
}  # fmt: skip

# look-alike confusions, applied to one occurrence at a time
CONFUSIONS = [
    ("l", "1"), ("1", "l"), ("l", "I"), ("I", "l"), ("O", "0"), ("0", "O"), ("o", "0"),
    ("rn", "m"), ("m", "rn"), ("cl", "d"), ("d", "cl"), ("u", "v"), ("v", "u"),
    ("e", "c"), ("c", "e"), ("a", "o"), ("o", "a"), ("h", "b"), ("n", "h"),
]  # fmt: skip
SUPER = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉", "01234567890123456789")
MATH = {"×": "x", "÷": "/", "≤": "<", "≥": ">", "≠": "=", "→": "-", "−": "-", "°": "", "Δ": "A",
        "μ": "u", "α": "a", "β": "B", "π": "n", "∑": "E", "√": "V"}  # fmt: skip
STRAY = list(".,'`|~;:-_")


def _confuse(word: str, rng: random.Random) -> str:
    options = [(a, b) for a, b in CONFUSIONS if a in word]
    if not options:
        return word
    a, b = rng.choice(options)
    pos = [m.start() for m in re.finditer(re.escape(a), word)]
    i = rng.choice(pos)
    return word[:i] + b + word[i + len(a) :]


def _lose_math(text: str, rate: float, rng: random.Random) -> str:
    """Drop carets and underscores (x^2 -> x2, H_2O -> H2O), flatten sub/superscripts."""
    if rng.random() > rate:
        return text
    text = re.sub(r"[\^_]\{?([^\s}]*)\}?", r"\1", text)
    text = text.translate(SUPER)
    return "".join(MATH.get(c, c) for c in text)


def noisy(text: str, level: str, seed: int = 0) -> str:
    """Return `text` with OCR-style errors. `level` is light, medium or heavy."""
    if level not in LEVELS:
        raise ValueError(f"Unknown noise level {level!r}. Use one of {sorted(LEVELS)}.")
    if not text.strip():
        return text
    p = LEVELS[level]
    rng = random.Random(f"{seed}:{level}:{text}")
    # math is lost per formula token so that one answer keeps some symbols at light levels
    tokens = [_lose_math(t, p["math"], rng) for t in text.split(" ")]
    out: list[str] = []
    for tok in tokens:
        core = tok.strip(".,;:!?()")
        if len(core) <= 3 and core.isalpha() and len(tokens) > 4 and rng.random() < p["drop"]:
            continue  # short word lost
        if any(c.isalpha() for c in tok):
            if rng.random() < p["conf"] * min(len(tok), 8) / 4:
                tok = _confuse(tok, rng)
            if len(tok) > 5 and rng.random() < p["split"]:
                k = rng.randint(2, len(tok) - 2)
                tok = tok[:k] + " " + tok[k:]
            elif len(tok) > 7 and rng.random() < p["hyph"]:
                k = rng.randint(3, len(tok) - 3)
                tok = tok[:k] + "-\n" + tok[k:]
        tok = re.sub(r"[.,;:!?]", lambda m: "" if rng.random() < p["punct"] else m.group(), tok)
        if rng.random() < p["stray"]:
            tok += rng.choice(STRAY)
        out.append(tok)
    res = ""
    for i, tok in enumerate(out):
        merge = i > 0 and rng.random() < p["merge"]
        res += tok if (i == 0 or merge) else " " + tok
    return res


def noisy_items(items: Sequence[Item], level: str, seed: int = 0) -> list[Item]:
    """Copies of `items` with only the student answer altered."""
    return [
        i.model_copy(update={"student_answer": noisy(i.student_answer, level, seed)}) for i in items
    ]

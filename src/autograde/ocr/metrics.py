"""Text-matching metrics for OCR output. Standard library only, so any environment can import it.

All scores compare the student's own words and numbers, as a bag of tokens, so they do not
depend on line order, line breaks or how an engine splits lines.
"""

from __future__ import annotations

import re
from collections import Counter
from difflib import SequenceMatcher

UNSURE = re.compile(r"\[\?([^\]?]*)\??\]")
FUZZY = 0.8  # similarity at which a token counts as a near match


def tokens(text: str) -> list[str]:
    text = UNSURE.sub(r"\1", text).replace("struck out:", " ")
    return [t for t in (w.strip(".,;:?!()'\"") for w in text.lower().split()) if t]


def similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def recall(truth: str, output: str, fuzzy: bool = False) -> float:
    """Share of the true tokens found in the output (a near match counts when fuzzy)."""
    want, have = Counter(tokens(truth)), Counter(tokens(output))
    hit = total = 0
    for tok, n in want.items():
        total += n
        found = min(n, have[tok])
        if fuzzy and found < n:
            pool = [h for h, c in have.items() if c > 0 and h != tok]
            extra = sum(1 for _ in range(n - found) if any(similar(tok, h) >= FUZZY for h in pool))
            found += extra
        hit += found
    return hit / max(total, 1)


def precision(truth: str, output: str) -> float:
    """Share of output tokens that are true tokens. Low means junk or printed text was read."""
    want, have = Counter(tokens(truth)), Counter(tokens(output))
    n = sum(have.values())
    return sum(min(c, want[t]) for t, c in have.items()) / n if n else 0.0


def squash(text: str) -> str:
    text = UNSURE.sub(r"\1", text).replace("→", "->").replace("−", "-")
    text = text.replace("\\lambda", "λ").replace("lambda", "λ").replace("{", "").replace("}", "")
    text = re.sub(r"(?<=\d)\s*,\s*(?=-?\d)", " ", text)  # [[1, 2], [3, 4]] equals [[1 2],[3 4]]
    return re.sub(r"[\s_]+", "", text).lower()  # a_12 and a12 are the same symbol


def _best_window(needle: str, hay: str) -> float:
    """Best similarity of `needle` to any window of `hay` of about the same length."""
    if not hay or not needle:
        return 0.0
    if needle in hay:
        return 1.0
    n, best = len(needle), 0.0
    for size in {max(n - 2, 1), n, n + 2}:
        for i in range(0, max(len(hay) - size, 0) + 1, max(n // 6, 1)):
            best = max(best, similar(needle, hay[i : i + size]))
    return best


def _numbers(text: str) -> str:
    """The numbers in `text`, space-separated and padded, so a row can be searched for."""
    return " " + " ".join(re.findall(r"-?\d+(?:\.\d+)?", text.replace("−", "-"))) + " "


def _matrix_found(fact: str, output: str) -> bool:
    """A written matrix [[a b],[c d]] is found when each of its rows appears as a run of numbers,
    whatever the layout (one line, one row per line, or matrices side by side)."""
    rows = re.findall(r"\[([^\[\]]+)\]", fact)
    if len(rows) < 2:
        return False
    stream = _numbers(output)
    return all(_numbers(row) in stream for row in rows)


def facts(strings: list[str], output: str, fuzzy: bool = False) -> float:
    """Share of key strings (formulas, matrices, conclusions) found, ignoring spaces and case."""
    hay = squash(output)
    ok = 0
    for s in strings:
        need = squash(s)
        ok += (
            need in hay
            or ("[[" in s and _matrix_found(s, output))
            or (fuzzy and _best_window(need, hay) >= FUZZY)
        )
    return ok / len(strings)

"""Offline stand-in for a language model: deterministic, no network, no API key.

`MockClient` lets the whole pipeline run end to end on a laptop, so a reviewer can reproduce the
demo and CI can smoke-test the real code paths. It is **not** a grader: it writes schemes by
splitting the model answer into sentences and marks by word overlap with them. Marks from it
only show that the plumbing works. Use a real backend for any actual marking.

Prompts are built from fixed templates (see ``prompts/``), so the mock reads the inputs it needs
back out of the user message. Requests it has no rule for get a minimal answer built from the
JSON schema, which satisfies validation but carries no meaning.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any, TypeVar

from pydantic import BaseModel

from autograde.llm.base import LLMClient, Usage

T = TypeVar("T", bound=BaseModel)

_STOP = frozenset(
    [
        "a",
        "an",
        "the",
        "of",
        "to",
        "in",
        "on",
        "at",
        "is",
        "are",
        "was",
        "were",
        "be",
        "by",
        "for",
        "and",
        "or",
        "it",
        "its",
        "this",
        "that",
        "with",
        "as",
        "from",
        "which",
        "can",
        "will",
        "not",
        "do",
        "does",
        "so",
        "than",
        "then",
        "into",
        "per",
        "each",
    ]
)
_VERDICT_LINE = re.compile(r"^(?P<id>[A-Z]\d+) \[(?P<status>\w+), [^\]]*\]: (?P<rest>.*)$")
_POINT_LINE = re.compile(r"^(?P<id>[A-Z]\d+) \((?P<marks>[\d.]+) marks\): (?P<desc>.*)$")


def _sentences(text: str) -> list[str]:
    """Split prose into sentences, dropping blanks and markdown bullets."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [p.strip(" -*\t") for p in parts if len(p.strip(" -*\t")) > 3]


def _words(text: str) -> set[str]:
    """Lower-case content words, with a crude plural strip so 'weights' matches 'weight'."""
    found = (w.rstrip("s") for w in re.findall(r"[a-zA-Z0-9]+", text.lower()))
    return {w for w in found if w and w not in _STOP}


def _between(text: str, start: str, *ends: str) -> str:
    """Text after the first `start` marker and before the earliest of the `ends` that follow."""
    if start not in text:
        return ""
    body = text.split(start, 1)[1]
    cuts = [body.index(e) for e in ends if e in body]
    return (body[: min(cuts)] if cuts else body).strip()


def _split_marks(total: float, n: int) -> list[float]:
    """Divide `total` marks into `n` positive parts that add up exactly."""
    step = round(total / n, 2)
    parts = [step] * (n - 1)
    parts.append(round(total - sum(parts), 6))
    return parts


def _rubric_draft(user: str) -> dict:
    """One scheme point per sentence of the model answer (at most four)."""
    total = float(_between(user, "Total marks:", "\n") or 1)
    answer = _between(user, "Model answer:", "\n\nTeacher's rubric:", "\n\nTotal marks:")
    sents = (_sentences(answer) or ["A correct answer"])[:4]
    marks = _split_marks(total, len(sents))
    return {
        "points": [
            {"id": f"P{i}", "description": s, "marks": m}
            for i, (s, m) in enumerate(zip(sents, marks, strict=True), 1)
        ]
    }


def _grading(user: str) -> dict:
    """Mark each scheme point met when the answer shares enough words with it."""
    scheme = _between(user, "Marking scheme:", "\n\nStudent answer:")
    answer = _between(user, "Student answer:", "\nMark the student answer.").split("\n\n")[0]
    sents = _sentences(answer)
    verdicts = []
    for line in scheme.splitlines():
        m = _POINT_LINE.match(line.strip())
        if not m:
            continue
        # Drop the rendered "Partial credit: ..." / "Final answer ..." notes so they cannot dilute
        # the overlap with the point's own wording.
        desc = re.split(r" Partial credit:| Final answer ", m["desc"])[0]
        need = _words(desc)
        best, best_hit = "", 0.0
        for s in sents:
            hit = len(need & _words(s)) / max(len(need), 1)
            if hit > best_hit:
                best, best_hit = s, hit
        met = best_hit >= 0.5 and best in answer
        verdicts.append(
            {
                "point_id": m["id"],
                "status": "met" if met else "not_met",
                "marks_awarded": float(m["marks"]) if met else 0.0,
                "evidence": best if met else "",
                "reason": "Matches the scheme point." if met else "Not found in the answer.",
            }
        )
    return {"verdicts": verdicts}


def _reading(user: str) -> dict:
    """A trivial first read: the first sentence is the gist, every sentence an idea."""
    sents = _sentences(_between(user, "Student answer:", "\n\n") or user) or ["(no answer)"]
    return {"gist": sents[0], "ideas": sents[:5], "problems": [], "form": "explanation"}


def _feedback(user: str) -> dict:
    """Praise the verdicts that were met and point at the ones that were not."""
    strengths, improvements = [], []
    for line in user.splitlines():
        m = _VERDICT_LINE.match(line.strip())
        if not m:
            continue
        if m["status"] == "met":
            strengths.append(f"You covered: {m['rest'].split('.')[0]}.")
        else:
            what = m["rest"].split(".")[0]
            improvements.append(
                {
                    "point_id": m["id"],
                    "kind": "missed",
                    "issue": f"The answer does not show: {what}.",
                    "why": "The marking scheme asks for this point.",
                    "fix": f"State clearly: {what}.",
                }
            )
    return {
        "asks": "",
        "strengths": strengths or ["You attempted the question."],
        "improvements": improvements,
        "summary": "Check the points listed above against the model answer.",
    }


def _review(_user: str) -> dict:
    return {"issues": [], "revised": None}


def _fill(schema: dict, defs: dict) -> Any:
    """Smallest value that satisfies a JSON schema (required fields only)."""
    if "$ref" in schema:
        return _fill(defs[schema["$ref"].rsplit("/", 1)[1]], defs)
    if "default" in schema:
        return schema["default"]
    for key in ("anyOf", "oneOf"):
        if key in schema:
            options = [o for o in schema[key] if o.get("type") != "null"] or schema[key]
            return _fill(options[0], defs)
    if "enum" in schema:
        return schema["enum"][0]
    kind = schema.get("type")
    if kind == "object":
        props = schema.get("properties", {})
        return {k: _fill(props[k], defs) for k in schema.get("required", []) if k in props}
    if kind == "array":
        need = schema.get("minItems", 0)
        return [_fill(schema.get("items", {}), defs) for _ in range(need)]
    if kind == "string":
        return "mock"
    if kind in ("integer", "number"):
        return schema.get("minimum", 0) if "exclusiveMinimum" not in schema else 1
    if kind == "boolean":
        return False
    return None


class MockClient(LLMClient):
    """Deterministic `LLMClient` that needs no model. See the module docstring for limits."""

    def __init__(self, model: str = "offline") -> None:
        """Register the answer rules; `model` only affects the cache label."""
        super().__init__(retries=0)
        self.model = model
        # Keyed by the pydantic class name so this module need not import every schema.
        self.rules: dict[str, Callable[[str], dict]] = {
            "RubricDraft": _rubric_draft,
            "Grading": _grading,
            "Reading": _reading,
            "Feedback": _feedback,
            "RubricReview": _review,
        }

    @property
    def name(self) -> str:
        """Cache label, e.g. 'mock-offline'."""
        return f"mock-{self.model}"

    def _complete(self, system: str, user: str, schema: dict) -> tuple[dict, Usage]:
        data = _fill(schema, schema.get("$defs", {}))
        return data, Usage(calls=1)

    def ask(self, system: str, user: str, model: type[T]) -> T:
        """Answer with the rule for `model` if there is one, else a schema-minimal value."""
        rule = self.rules.get(model.__name__)
        if rule is None:
            data, usage = self._complete(system, user, model.model_json_schema())
        else:
            data, usage = rule(user), Usage(calls=1)
        with self._lock:
            self.usage.add(usage)
        return model.model_validate(data)

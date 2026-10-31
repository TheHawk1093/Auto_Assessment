"""The teacher's marking settings, described once.

The settings tab draws its widgets from FIELDS and the job runner builds its command-line flags
from the same list. To add a setting: add the flag to `autograde exam` (src/autograde/cli/exam.py),
then add one `Field` here. Nothing else changes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from app.text import normalize

Kind = Literal["select", "number", "int", "text", "textarea", "bool", "lines", "per_question"]


@dataclass(frozen=True)
class Field:
    """One teacher setting: its widget (key, label, kind, default) and the CLI flag it becomes."""

    key: str
    label: str
    kind: Kind
    default: Any
    flag: str  # the `autograde exam` flag this becomes
    help: str = ""
    options: dict[str, Any] | None = None  # select: label shown -> value stored
    group: str = "marks"  # which block of the page it sits in (see views/teacher/settings.py)
    placeholder: str = ""


FIELDS: list[Field] = [
    Field(
        "granularity", "Part marks", "select", None, "--granularity",
        "How partial marks may be given.",
        options={
            "As per the rubric": None,
            "Whole marks only (all or nothing)": "none",
            "Half of a point's marks (50%)": "half",
            "Quarter steps (25%, 50%, 75%)": "quarter",
        },
    ),
    Field(
        "mark_step", "Custom step in marks", "number", None, "--mark-step",
        "For example 0.5 allows 1.5 out of 2. Replaces the choice above.",
    ),
    Field(
        "strictness", "Strictness", "select", None, "--strictness", "",
        options={"Default": None, "Lenient": "lenient", "Moderate": "moderate", "Strict": "strict"},
    ),
    Field(
        "count_best", "Number of questions that count", "int", None,
        "--count-best", "Only the best scores count. Leave off if every question counts.",
    ),
    Field(
        "note", "Instructions for the marker", "textarea", "", "--note",
        group="notes", placeholder="e.g. Units are required. Accept either sign convention.",
    ),
    Field("question_notes", "Notes for single questions", "per_question", {},
          "--question-note", group="notes"),
    Field(
        "struck_out", "Questions a student crossed out", "lines",
        [], "--struck-out", "These are not marked.", group="notes", placeholder="21ME004=3",
    ),
    Field("allow_unresolved", "Mark sheets even if the student is unknown", "bool", False,
          "--allow-unresolved", group="toggles"),
    Field("working_required", "Numerical answers need working", "bool", False,
          "--working-required", group="toggles"),
    Field("no_follow_through", "No credit for follow-through errors", "bool", False,
          "--no-follow-through", group="toggles"),
    Field("code_exec", "Run students' code (Python)", "bool",
          False, "--code-exec", "Runs against your tests in a sealed sandbox.", group="toggles"),
    Field("ignore_rubric_rules", "Ignore rules written in the paper", "bool", False,
          "--ignore-rubric-rules", group="toggles"),
]  # fmt: skip

BY_KEY = {f.key: f for f in FIELDS}


def defaults() -> dict:
    """Return every setting's default value, keyed by setting."""
    return {f.key: f.default for f in FIELDS}


def cli_args(settings: dict) -> list[str]:
    """The `autograde exam` flags for these settings. Unset or empty settings add nothing."""
    out: list[str] = []
    for f in FIELDS:
        value = settings.get(f.key, f.default)
        if f.kind == "bool":
            if value:
                out.append(f.flag)
        elif f.kind == "lines":
            for line in value or []:
                out += [f.flag, normalize(line).strip()]
        elif f.kind == "per_question":
            for qid, text in (value or {}).items():
                if text.strip():
                    out += [f.flag, f"{qid}={normalize(text).strip()}"]
        elif value not in (None, "", 0, 0.0):
            out += [f.flag, normalize(str(value)).strip()]
    return out

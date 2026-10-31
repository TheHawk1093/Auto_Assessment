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
        "granularity", "Mark granularity", "select", None, "--granularity",
        "How partial marks may be given.",
        options={
            "Let the rubric decide": None,
            "Only the part marks the rubric names": "stated",
            "Whole marks only": "none",
            "Halves": "half",
            "Quarters": "quarter",
        },
    ),
    Field(
        "mark_step", "Marks come in multiples of (0 = off)", "number", None, "--mark-step",
        "0.5 allows 1.5 out of 2; 0.2 allows 1.8. Overrides granularity when set.",
    ),
    Field(
        "strictness", "Grading strictness", "select", None, "--strictness", "",
        options={"Default": None, "Lenient": "lenient", "Moderate": "moderate", "Strict": "strict"},
    ),
    Field(
        "count_best", "Best-of-n: only the best N questions count (0 = all)", "int", None,
        "--count-best", "Read from the paper when it says so; set here to override.",
    ),
    Field(
        "note", "General guidelines for the marker", "textarea", "", "--note",
        group="notes", placeholder="e.g. Units are required. Accept either sign convention.",
    ),
    Field("question_notes", "Notes for individual questions", "per_question", {},
          "--question-note", group="notes"),
    Field(
        "struck_out", "Questions a student struck out (one per line, STUDENT=QUESTION)", "lines",
        [], "--struck-out", "These are not marked.", group="notes", placeholder="21ME004=3",
    ),
    Field("allow_unresolved", "Mark even if some sheets are unattributed", "bool", False,
          "--allow-unresolved", group="toggles"),
    Field("working_required", "Working required for numerical answers", "bool", False,
          "--working-required", group="toggles"),
    Field("no_follow_through", "Do not credit follow-through from earlier parts", "bool", False,
          "--no-follow-through", group="toggles"),
    Field("ignore_rubric_rules", "Ignore rules written in the paper and rubric", "bool", False,
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

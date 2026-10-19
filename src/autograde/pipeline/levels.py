"""Strictness levels. A rubric written at a level makes the grader follow that level.

The level decides which marking policy the grader uses and how much a "partial" verdict is
worth, so a harsher rubric really does mark harder instead of only reading harder.
"""

from __future__ import annotations

from autograde import prompts

LEVELS = ("lenient", "moderate", "harsh")
LEVEL_POLICY = {"lenient": "essence", "moderate": "balanced", "harsh": "strict"}
LEVEL_PARTIAL_WEIGHT = {"lenient": 0.9, "moderate": 0.7, "harsh": 0.5}


def dataset_of(question_key: str) -> str:
    return question_key.split("/", 1)[0]


def dataset_policy(dataset: str) -> str:
    """How a dataset's teacher marks, written from marked examples. Empty if there is none."""
    try:
        return prompts.system(f"policy.{dataset}")
    except FileNotFoundError:
        return ""


def level_prompt(level: str, dataset: str) -> str:
    """The rubric-writing instructions for one level of one dataset."""
    parts = [prompts.system("rubric.levels"), prompts.system(f"rubric.level.{level}")]
    policy = dataset_policy(dataset)
    if policy:
        parts.append("How this exam is marked, and what each level means here:\n" + policy)
    parts.append(f"Write the rubric at the {level.upper()} level.")
    return "\n\n".join(parts)

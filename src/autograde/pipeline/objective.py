"""Multiple choice, checked by code.

No model marks a choice; a model only explains a wrong one (see `feedback.write_mcq_feedback`).

The student's answer may be a letter, "(b)", "Option B", "B. Random Forest", the option's own
words, or, for a question that allows several, "A and C". Anything that cannot be read as exactly
the right choices earns nothing and is flagged for the teacher: an unclear or double choice is a
reading problem to look at, never a guess.
"""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import (
    Grading,
    Item,
    PointVerdict,
    Question,
    Rubric,
    RubricPoint,
    RubricRecord,
)

LABEL = r"[A-Ha-h1-9]"
_LINE_OPTION = re.compile(rf"^\s*\(?({LABEL})[\).:\]]\s+(\S.*)$", re.M)
_INLINE_OPTION = re.compile(r"\(([a-hA-H1-9])\)\s*([^()]+?)(?=\s*\([a-hA-H1-9]\)|$)")
_MARKED = re.compile(
    rf"(?:answer|ans|option|choice|correct|chose|choose|select(?:ed)?)\s*(?:is|are|=|:)?\s*"
    rf"\(?({LABEL})\b(?:\s*(?:,|and|&)\s*\(?({LABEL})\b)*",
    re.I,
)
_SHORT = re.compile(rf"^\W*\(?({LABEL})\)?(?:\s*(?:,|and|&|/|\+)?\s*\(?({LABEL})\)?)*\W*$", re.I)


_RUN_LABEL = re.compile(rf"(?:(?<=\s)|^)\(?({LABEL})[\).:]\s+")


def _run_of_labels(question: str) -> dict[str, str]:
    """Split options written one after another on a single line.

    For example "A. SVM B. Random Forest C. KNN", as happens when a paper is read from a
    document. Only a run of consecutive labels that starts
    at A (or 1) counts, so a sentence that happens to contain "A." is not read as an option.
    """
    marks = list(_RUN_LABEL.finditer(question))
    for start, first in enumerate(marks):
        if first.group(1).upper() not in ("A", "1"):
            continue
        run = [first]
        for m in marks[start + 1 :]:
            if ord(m.group(1).upper()) == ord(run[-1].group(1).upper()) + 1:
                run.append(m)
        if len(run) >= 3:  # a real multiple-choice question has at least three options
            ends = [m.start() for m in run[1:]] + [len(question)]
            return {
                m.group(1).upper(): question[m.end() : end].strip()
                for m, end in zip(run, ends, strict=True)
            }
    return {}


def parse_options(question: str) -> dict[str, str]:
    """The option labels and texts printed in the question (a-d, A-D or 1-4)."""
    found = {m.group(1).upper(): m.group(2).strip() for m in _LINE_OPTION.finditer(question)}
    if len(found) < 2:
        found = {m.group(1).upper(): m.group(2).strip() for m in _INLINE_OPTION.finditer(question)}
    if len(found) < 2:
        found = _run_of_labels(question)
    return found if len(found) >= 2 else {}


def _norm(text: str) -> str:
    return re.sub(r"[\W_]+", " ", text.lower()).strip()


def choices_in(text: str, options: dict[str, str]) -> set[str]:
    """The option labels a piece of text picks, upper case; empty when none can be told."""
    text = text.strip()
    if not text:
        return set()
    labels = {k.upper() for k in options} if options else None

    def keep(found: set[str]) -> set[str]:
        return {c for c in found if labels is None or c in labels}

    if _SHORT.match(text):  # a bare "B", "(c)", "A, C", "a and c"
        return keep({c.upper() for c in re.findall(rf"\b({LABEL})\b", text)})
    marked = _MARKED.search(text)
    if marked:  # "the answer is C", "I choose A and C"
        after = re.sub(r"^[A-Za-z]+\s*(?:is|are|=|:)?\s*", "", marked.group(0), flags=re.I)
        return keep({c.upper() for c in re.findall(rf"\b({LABEL})\b", after)})
    lead = re.match(rf"^\W*\(?({LABEL})[\).:]\s", text)  # "B. Random forest"
    if lead:
        return keep({lead.group(1).upper()})
    wanted = _norm(text)  # the option's own words
    hits = {k.upper() for k, v in options.items() if _norm(v) and _norm(v) == wanted}
    if not hits and len(wanted.split()) <= 4:  # a short phrase, not an explanation that mentions it
        hits = {
            k.upper()
            for k, v in options.items()
            if len(_norm(v)) >= 4
            and _norm(v) in wanted
            and len(wanted.split()) <= len(_norm(v).split()) + 2
        }
    return hits if len(hits) == 1 else set()


class Choice(BaseModel):
    """The model's pick of the correct option when the paper gives no key."""

    option: str = Field(description="The label of the single best option, such as B.")
    reason: str = Field(description="One sentence on why it is correct.")


def mcq_rubric(question: Question, derived_key: str = "") -> Rubric:
    """Build the one-point scheme for a choice from the key (or the derived key)."""
    key = choices_in(question.model_answer, parse_options(question.text)) or (
        {derived_key.upper()} if derived_key else set()
    )
    what = f"Chooses {' and '.join(sorted(key))}" if key else "Chooses the correct option"
    note = "Objective question: the choice is checked by code, all or nothing."
    if derived_key:
        note += " No answer key was given: the model chose it, so check it."
    return Rubric(
        points=[RubricPoint(id="P1", description=what, marks=question.max_mark)],
        notes=note,
        answer_key=derived_key.upper(),
    )


def mcq_record(question: Question, client: LLMClient | None = None) -> RubricRecord:
    """Build the one-point scheme for a choice.

    With no answer key in the question, the model chooses the option once (and the scheme says
    so), so a paper without a key can still be marked.
    """
    derived, review = "", []
    if client is not None and not choices_in(question.model_answer, parse_options(question.text)):
        options = parse_options(question.text)
        if options:
            picked = client.ask(prompts.system("mcq.key"), question.text, Choice).option
            derived = next(iter(choices_in(picked, options)), "")
            if derived:
                review = [f"No answer key was given; the model chose {derived}. Please check it."]
    return RubricRecord(
        question_key=question.key,
        rubric=mcq_rubric(question, derived),
        selftest_passed=True,
        review_notes=review,
    )


def mark_mcq(item: Item, rubric: Rubric) -> tuple[Grading, list[str]]:
    """Mark a choice all or nothing.

    Flags: `unclear_choice` (nothing readable), `multiple_choices` (more than
    allowed), `mcq_key_unreadable` (the model answer names no option).
    """
    options = parse_options(item.question)
    truth = choices_in(item.model_answer, options)
    got = choices_in(item.student_answer, options)
    point = rubric.points[0].id
    flags: list[str] = ["mcq_key_derived"] if rubric.answer_key else []
    if not truth:
        status, reason = (
            "not_met",
            "The answer key does not name an option, so this needs checking.",
        )
        flags.append("mcq_key_unreadable")
    elif not got:
        status, reason = "not_met", "No clear choice was found in the answer."
        flags.append("unclear_choice")
    elif got == truth:
        status, reason = "met", f"Chose {' and '.join(sorted(got))}, which is correct."
    elif len(got) > len(truth):
        status = "not_met"
        reason = f"More options were chosen ({', '.join(sorted(got))}) than are allowed."
        flags.append("multiple_choices")
    else:
        status = "not_met"
        picked, right = " and ".join(sorted(got)), " and ".join(sorted(truth))
        reason = f"Chose {picked}; the correct choice is {right}."
    marks = rubric.points[0].marks if status == "met" else 0.0
    verdict = PointVerdict(
        point_id=point,
        status=status,
        marks_awarded=marks,
        evidence=item.student_answer.strip()[:80] if status == "met" else "",
        reason=reason,
    )
    return Grading(verdicts=[verdict]), flags

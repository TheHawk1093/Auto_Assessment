"""Stage 5: write feedback for the student from the checked marking."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel

from autograde import prompts
from autograde.llm import LLMClient
from autograde.localize import words
from autograde.schemas import EPS, Feedback, Grading, Improvement, Item, Rubric, effective_kind
from autograde.textutil import leakage

MAX_WORDS = 220
LONG_WORDS = 240  # a first draft longer than this is rewritten once (formal median is ~180)
STYLES = (
    "hints",
    "formal",
    "concrete",
    "brief",
    "detailed",
    "coach",
)  # one call each, own prompt file
LEAK_LIMIT = {"hints": 0.1}  # share of the model answer's phrases allowed in the feedback
DEFAULT_LEAK_LIMIT = 0.35


class Pick(BaseModel):
    choice: int  # 1-based number of the best draft
    reason: str


def feedback_words(fb: Feedback) -> int:
    parts = [fb.asks, *fb.strengths, fb.summary]
    for x in fb.improvements:
        parts += [x.issue, x.why, x.fix]
    return sum(len(p.split()) for p in parts)


def problems(fb: Feedback, item: Item, grading: Grading, rubric: Rubric, variant: str) -> list[str]:
    """Cheap checks done in code: the feedback must cover exactly the points that lost marks."""
    full = {p.id: p.marks for p in rubric.points}
    lost = {
        v.point_id for v in grading.verdicts if v.marks_awarded < full.get(v.point_id, 0) - 1e-9
    }
    said = {x.point_id for x in fb.improvements}
    out = [f"missing:{p}" for p in sorted(lost - said)]
    out += [f"extra:{p}" for p in sorted(said - lost)]
    if any(not x.why.strip() for x in fb.improvements):
        out.append("no_why")
    if feedback_words(fb) > MAX_WORDS:
        out.append("too_long")
    text = " ".join(
        [*fb.strengths, fb.summary, *(f"{x.issue} {x.why} {x.fix}" for x in fb.improvements)]
    )
    if leakage(text, item.model_answer) > LEAK_LIMIT.get(variant, DEFAULT_LEAK_LIMIT):
        out.append("gives_away_answer")
    return out


def language_note(language: str) -> str:
    """How to write in a language: the general note, then `language.<language>` if the
    language needs its own (kept apart from the English prompts, which never see this)."""
    if not language:
        return ""
    own = prompts.optional(f"language.{language.lower()}")
    general = prompts.render("language.feedback.system", language=language)
    return "\n\n".join(filter(None, [general, own]))


def _system(name: str, stance: bool, kind: str = "", language: str = "") -> str:
    """A style's instructions, plus the note on matching the marking stance when there is one, the
    guidance for this kind of question (`feedback.kind.<kind>.system.md`, if it exists) and the
    language to write in."""
    parts = [prompts.system(name)]
    if stance:
        parts.append(prompts.system("feedback.stance"))
    if kind and (extra := prompts.optional(f"feedback.kind.{kind}")):
        parts.append(extra)
    if note := language_note(language):
        parts.append(note)
    return "\n\n".join(parts)


def _draft(values: dict, variant: str, client: LLMClient, stance: bool = False) -> Feedback:
    """standard | hints | formal: one call. critique: a standard draft, then a review pass."""
    user = prompts.render("feedback.user", **values)
    kind, language = values.get("kind", ""), values.get("language", "")
    if variant in STYLES:
        return client.ask(_system(f"feedback.{variant}", stance, kind, language), user, Feedback)
    draft = client.ask(_system("feedback", stance, kind, language), user, Feedback)
    if variant == "standard":
        return draft
    critique_user = prompts.render(
        "feedback.critique.user", draft=draft.model_dump_json(indent=2), **values
    )
    return client.ask(prompts.system("feedback.critique"), critique_user, Feedback)


def first_sentence(text: str) -> str:
    """Up to the first full stop that ends a sentence (not the one in 'e.g.' or 'i.e.')."""
    safe = text.replace("e.g.", "e.g\0").replace("i.e.", "i.e\0")
    return safe.split(". ")[0].rstrip(".").replace("\0", ".")


def full_marks_feedback(rubric: Rubric, grading: Grading, language: str = "") -> Feedback:
    """Feedback for a full-mark answer, built without a model: what was right, in their words."""
    by_id = {p.id: p for p in rubric.points}
    strengths = []
    for v in grading.verdicts:
        what = by_id[v.point_id].description if v.point_id in by_id else v.point_id
        said = " ".join(v.evidence.split()[:30]) if v.evidence else ""
        idea = first_sentence(what)  # the idea only, not the scheme's notes on wording
        w = words(language)
        strengths.append(
            w["wrote"].format(said=said, idea=idea) if said else w["covered"].format(idea=idea)
        )
    return Feedback(
        strengths=strengths,
        improvements=[],
        summary=words(language)["full"],
        language=language,
    )


_ENGLISH_OPENER = re.compile(r"^\s*Overall[,:]?\s+")


def _finish(fb: Feedback, language: str) -> Feedback:
    """Mark the language, and drop an English 'Overall,' that the model kept in front of a summary
    written in the student's language (the labels are added in that language by `Feedback.text`)."""
    if not language:
        return fb
    return fb.model_copy(
        update={"language": language, "summary": _ENGLISH_OPENER.sub("", fb.summary)}
    )


def write_feedback(
    item: Item,
    rubric: Rubric,
    grading: Grading,
    client: LLMClient,
    variant: str = "standard",
    n: int = 1,
    notes: str = "",
    language: str = "",
    evidence: str = "",
) -> Feedback:
    """Feedback for one marked answer, in `language` when one is given (see `_write`)."""
    fb = _write(item, rubric, grading, client, variant, n, notes, language, evidence)
    return _finish(fb, language)


def _write(
    item: Item,
    rubric: Rubric,
    grading: Grading,
    client: LLMClient,
    variant: str = "standard",
    n: int = 1,
    notes: str = "",
    language: str = "",
    evidence: str = "",
) -> Feedback:
    """standard: what is missing and the fix | hints: guide towards the missing idea | critique:
    draft then review | formal: examiner-report register.

    With n > 1, n drafts are written, drafts that fail the code checks are dropped, and the
    model picks the best of what is left. `notes` are the teacher's instructions for this
    question; a multiple-choice question gets its own explanation of the wrong choice.
    """
    if not item.student_answer.strip():
        return Feedback(
            strengths=[],
            improvements=[],
            summary=words(language)["empty"],
        )
    if grading.total >= item.max_mark - EPS:
        return full_marks_feedback(rubric, grading, language)
    if item.kind == "mcq":
        return write_mcq_feedback(item, grading, client, notes)
    teacher = f"Teacher's instructions for this question: {notes}" if notes.strip() else ""
    if evidence.strip():
        teacher = (
            f"{teacher}\nFacts checked by code (state them as they are; never contradict "
            f"them):\n{evidence.strip()}"
        ).strip()
    if language:
        teacher = (
            f"{teacher}\nWrite all the feedback text in {language}, including the fixed opening "
            "phrases (such as 'The question asks you to' and 'Overall,'), translated naturally."
        ).strip()
    values = dict(
        question=item.question,
        model_answer=item.model_answer,
        student_answer=item.student_answer,
        total=f"{grading.total:g}",
        max_mark=f"{item.max_mark:g}",
        kind=effective_kind(item.kind, rubric),
        language=language,
        extra=teacher,
        marking="\n".join(filter(None, [rubric.stance(), grading.render(rubric)])),
    )
    stance = bool(rubric.level)
    if n <= 1:
        draft = _draft(values, variant, client, stance)
        if feedback_words(draft) > LONG_WORDS:  # one retry: too long to read at a glance
            note = (
                f"Your previous draft had {feedback_words(draft)} words. Rewrite it in under "
                f"{MAX_WORDS}, keeping only the most important points."
            )
            shorter = _draft(
                {**values, "extra": f"{teacher}\n{note}".strip()}, variant, client, stance
            )
            draft = min(draft, shorter, key=feedback_words)
        return draft
    with ThreadPoolExecutor(n) as pool:
        drafts = list(pool.map(lambda _: _draft(values, variant, client, stance), range(n)))
    clean = [d for d in drafts if not problems(d, item, grading, rubric, variant)]
    choices = clean or drafts  # if every draft has a problem, still pick the best of them
    if len(choices) == 1:
        return choices[0]
    numbered = "\n\n".join(
        f"Draft {i}:\n{d.model_dump_json(indent=2)}" for i, d in enumerate(choices, 1)
    )
    user = prompts.render("feedback.pick.user", drafts=numbered, **values)
    choice = client.ask(prompts.system("feedback.pick"), user, Pick).choice
    return choices[min(max(choice, 1), len(choices)) - 1]


def write_mcq_feedback(
    item: Item, grading: Grading, client: LLMClient, notes: str = ""
) -> Feedback:
    """Feedback for a wrong or unreadable multiple-choice answer. The choice and the right option
    are facts from code; the model only explains why the right option is right and why the
    chosen one tempts and fails. An unreadable choice needs no model: it asks for a clear one."""
    reason = grading.verdicts[0].reason if grading.verdicts else ""
    if "No clear choice" in reason or "More options" in reason:
        issue = "No single clear choice could be read from your answer."
        if "More options" in reason:
            issue = "More options were marked than the question allows."
        return Feedback(
            asks="The question asks you to choose the correct option.",
            strengths=[],
            improvements=[
                Improvement(
                    point_id=grading.verdicts[0].point_id,
                    kind="incorrect",
                    issue=issue,
                    why="An answer that cannot be read as one choice cannot be marked as correct.",
                    fix="Write only the letter of your chosen option, clearly.",
                )
            ],
            summary="Overall, mark one option clearly so that your answer can be read.",
        )
    user = prompts.render(
        "feedback.mcq.user",
        question=item.question,
        model_answer=item.model_answer,
        student_answer=item.student_answer,
        result=reason,
        notes=notes,
    )
    return client.ask(prompts.system("feedback.mcq"), user, Feedback)

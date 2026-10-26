"""Stage 5: write feedback for the student from the checked marking."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from pydantic import BaseModel

from autograde import prompts
from autograde.llm import LLMClient
from autograde.schemas import EPS, Feedback, Grading, Item, Rubric
from autograde.textutil import leakage

MAX_WORDS = 220
LONG_WORDS = 240  # a first draft longer than this is rewritten once (formal median is ~180)
STYLES = ("hints", "formal", "brief", "detailed", "coach")  # one call each, own prompt file
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


def _system(name: str, stance: bool) -> str:
    """A style's instructions, plus the note on matching the marking stance when there is one."""
    text = prompts.system(name)
    return text + "\n\n" + prompts.system("feedback.stance") if stance else text


def _draft(values: dict, variant: str, client: LLMClient, stance: bool = False) -> Feedback:
    """standard | hints | formal: one call. critique: a standard draft, then a review pass."""
    user = prompts.render("feedback.user", **values)
    if variant in STYLES:
        return client.ask(_system(f"feedback.{variant}", stance), user, Feedback)
    draft = client.ask(_system("feedback", stance), user, Feedback)
    if variant == "standard":
        return draft
    critique_user = prompts.render(
        "feedback.critique.user", draft=draft.model_dump_json(indent=2), **values
    )
    return client.ask(prompts.system("feedback.critique"), critique_user, Feedback)


def full_marks_feedback(rubric: Rubric, grading: Grading) -> Feedback:
    """Feedback for a full-mark answer, built without a model: what was right, in their words."""
    by_id = {p.id: p for p in rubric.points}
    strengths = []
    for v in grading.verdicts:
        what = by_id[v.point_id].description if v.point_id in by_id else v.point_id
        said = " ".join(v.evidence.split()[:30]) if v.evidence else ""
        idea = what.split(". ")[0].rstrip(".")  # the idea only, not the scheme's notes on wording
        strengths.append(
            f'You wrote "{said}", which covers: {idea}.' if said else f"Covered: {idea}."
        )
    return Feedback(
        strengths=strengths,
        improvements=[],
        summary="Overall, this response earned full marks and needs no changes.",
    )


def write_feedback(
    item: Item,
    rubric: Rubric,
    grading: Grading,
    client: LLMClient,
    variant: str = "standard",
    n: int = 1,
) -> Feedback:
    """standard: what is missing and the fix | hints: guide towards the missing idea | critique:
    draft then review | formal: examiner-report register.

    With n > 1, n drafts are written, drafts that fail the code checks are dropped, and the
    model picks the best of what is left.
    """
    if not item.student_answer.strip():
        return Feedback(
            strengths=[],
            improvements=[],
            summary="No answer was given for this question, so no marks could be awarded.",
        )
    if grading.total >= item.max_mark - EPS:
        return full_marks_feedback(rubric, grading)
    values = dict(
        question=item.question,
        model_answer=item.model_answer,
        student_answer=item.student_answer,
        total=f"{grading.total:g}",
        max_mark=f"{item.max_mark:g}",
        extra="",
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
            shorter = _draft({**values, "extra": note}, variant, client, stance)
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

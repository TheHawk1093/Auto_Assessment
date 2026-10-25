"""Typed data contracts shared by every stage of the pipeline."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

EPS = 1e-6


class Item(BaseModel):
    """One student's answer to one question, plus the teacher's mark when the dataset has it."""

    id: str
    dataset: str
    question_id: str
    question: str
    model_answer: str
    student_answer: str
    max_mark: float = Field(gt=0)
    human_mark: float | None = None
    human_feedback: str | None = None
    labels: dict[str, str] = Field(
        default_factory=dict,
        description="The teacher's verdict per rubric point (met, partial, not_met), if known.",
    )

    @property
    def question_key(self) -> str:
        return f"{self.dataset}/{self.question_id}"


class Question(BaseModel):
    """A question with its model answer. Marking schemes are made once per question."""

    key: str
    text: str
    model_answer: str
    max_mark: float = Field(gt=0)


class RubricPoint(BaseModel):
    id: str = Field(description="Short id such as P1, P2.")
    description: str = Field(description="One checkable thing a correct answer contains.")
    marks: float = Field(gt=0, description="Marks for this point when fully met.")
    partial_credit: str = Field(
        default="", description="When half-credit applies, if at all. Empty if all-or-nothing."
    )


class Rubric(BaseModel):
    """The marking scheme: a short list of points whose marks add up to the question total."""

    points: list[RubricPoint] = Field(min_length=1)
    notes: str = Field(
        default="",
        description="Two or three plain sentences: what earns full, part and no marks.",
    )
    policy: Literal["literal", "essence", "balanced", "strict"] | None = Field(
        default=None, description="How tightly to judge a point. Overrides the level and config."
    )
    partial_weight: float | None = Field(
        default=None, ge=0, le=1, description="Share of a point's marks for a partial verdict."
    )
    level: Literal["lenient", "moderate", "harsh"] | None = Field(
        default=None, description="Set by code: the strictness this rubric was written at."
    )

    @model_validator(mode="after")
    def _unique_ids(self) -> Rubric:
        ids = [p.id for p in self.points]
        if len(set(ids)) != len(ids):
            raise ValueError(f"Duplicate point ids: {ids}")
        return self

    @property
    def total(self) -> float:
        return round(sum(p.marks for p in self.points), 6)

    def stance(self) -> str:
        """The strictness and notes, as a short header for the marker. Empty if there are none."""
        if not self.level and not self.notes:
            return ""
        return f"Marking stance: {self.level or 'standard'}. {self.notes}".strip()

    def render(self) -> str:
        lines = [self.stance()] if self.stance() else []
        for p in self.points:
            note = f" Partial credit: {p.partial_credit}" if p.partial_credit else ""
            lines.append(f"{p.id} ({p.marks:g} marks): {p.description}{note}")
        return "\n".join(lines)


class RubricRecord(BaseModel):
    """A cached marking scheme with the outcome of its automatic self-test."""

    question_key: str
    rubric: Rubric
    selftest_passed: bool | None = None
    selftest_notes: list[str] = Field(default_factory=list)


Status = Literal["met", "partial", "not_met"]


class PointVerdict(BaseModel):
    point_id: str
    status: Status
    marks_awarded: float = Field(ge=0)
    model_marks: float | None = Field(
        default=None, description="Set by code: the marks the model first proposed."
    )
    evidence: str = Field(
        default="", description="Exact words copied from the student answer. Empty if not_met."
    )
    reason: str = Field(description="One sentence explaining the verdict.")


class Grading(BaseModel):
    verdicts: list[PointVerdict]

    @property
    def total(self) -> float:
        return round(sum(v.marks_awarded for v in self.verdicts), 6)

    def render(self, rubric: Rubric) -> str:
        """Verdicts next to their scheme points, for use in later prompts."""
        by_id = {p.id: p for p in rubric.points}
        lines = []
        for v in self.verdicts:
            p = by_id.get(v.point_id)
            what = p.description if p else v.point_id
            worth = f"{p.marks:g}" if p else "?"
            quote = f' Student wrote: "{v.evidence}".' if v.evidence else ""
            lines.append(
                f"{v.point_id} [{v.status}, {v.marks_awarded:g}/{worth}]: {what}.{quote} {v.reason}"
            )
        return "\n".join(lines)


class Improvement(BaseModel):
    point_id: str
    kind: Literal["partial", "missed", "incorrect"] = Field(
        default="missed",
        description=(
            "partial: stated, but not to the standard. missed: left out. "
            "incorrect: stated, but wrong or misapplied."
        ),
    )
    issue: str = Field(description="What is missing or wrong, in plain words.")
    why: str = Field(
        default="",
        description="Why the missing idea matters or why the student's version is wrong.",
    )
    fix: str = Field(description="A concrete change the student can make next time.")


class Feedback(BaseModel):
    asks: str = Field(default="", description="What the question asks for, in one sentence.")
    strengths: list[str] = Field(description="What the student did well, tied to their own words.")
    improvements: list[Improvement]
    summary: str = Field(description="One or two sentences the student should remember.")

    def text(self) -> str:
        """The feedback as plain text, in the order the student reads it."""
        labels = {"partial": "Partly there", "missed": "Missed", "incorrect": "Incorrect"}
        parts = [self.asks] if self.asks else []
        parts += [f"What you did well: {s}" for s in self.strengths]
        for x in self.improvements:
            body = " ".join(p for p in (x.issue, x.why, x.fix) if p)
            parts.append(f"{labels[x.kind]}: {body}")
        parts.append(self.summary)
        return "\n".join(parts)


class Reading(BaseModel):
    """A first pass over the student's answer alone, before any marking."""

    gist: str = Field(description="What the student is saying, in one or two plain sentences.")
    ideas: list[str] = Field(description="Each distinct idea or step stated, in your own words.")
    problems: list[str] = Field(
        description="Anything unclear, contradictory or wrong by general knowledge. Empty if none."
    )
    form: Literal["explanation", "short_answer", "keyword_list", "incoherent"] = Field(
        default="explanation",
        description=(
            "explanation: connected statements, even if poorly written. short_answer: a word, "
            "number, formula, phrase or list of items that answers a question asking for just "
            "that. keyword_list: a bare list of terms where an explanation was asked. "
            "incoherent: scrambled or meaningless text from which no claim can be read."
        ),
    )


class Result(BaseModel):
    """Everything produced for one student answer."""

    item: Item
    mode: Literal["pipeline", "baseline"]
    predicted_mark: float
    reading: Reading | None = None
    grading: Grading | None = None
    feedback: Feedback | None = None
    second_mark: float | None = Field(
        default=None, description="Mark from the second model, when one is configured."
    )
    votes: list[float] = Field(
        default_factory=list, description="Total of each marking when voting (votes > 1)."
    )
    flags: list[str] = Field(default_factory=list)

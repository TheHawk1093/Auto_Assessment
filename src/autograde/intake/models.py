"""The exam as the teacher gives it: a question paper, reference files, student answers."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from autograde.schemas import Kind


class QuestionSpec(BaseModel):
    """One question that carries its own marks. A sub-question is a question of its own."""

    id: str = Field(description="Printed number and letter without punctuation: 1, 2a, 3bii.")
    text: str = Field(description="The full text to answer, with any shared stem before it.")
    max_mark: float = Field(gt=0, description="Marks printed for this question or sub-question.")
    kind: Kind = Field(
        default="short",
        description="short: a word to a paragraph. essay: long free writing. "
        "maths: a worked solution or proof. numeric: a calculation whose final answer is a "
        "number with a unit. mcq: choose an option from those printed. code: write a program or "
        "code. diagram: draw a figure, graph or circuit.",
    )
    field: str = Field(default="", description="Subject area in one or two words.")


class Paper(BaseModel):
    """The question paper: a title and its questions in order."""

    title: str = ""
    questions: list[QuestionSpec] = Field(min_length=1)

    @model_validator(mode="after")
    def _unique_ids(self) -> Paper:
        ids = [q.id for q in self.questions]
        dupes = sorted({i for i in ids if ids.count(i) > 1})
        if dupes:
            raise ValueError(f"Question ids used more than once: {dupes}")
        return self

    @property
    def total(self) -> float:
        """Return the paper's total marks."""
        return round(sum(q.max_mark for q in self.questions), 6)

    @property
    def ids(self) -> list[str]:
        """Return the question ids in paper order."""
        return [q.id for q in self.questions]


class Reference(BaseModel):
    """What the teacher supplied for one question. Either part may be missing."""

    model_answer: str = ""
    rubric: str = ""
    tests: str = ""  # code questions: one assert per line


class ExamRules(BaseModel):
    """Marking rules that the paper's instructions or the teacher's rubric state for the whole exam.

    Nothing here is guessed: a field keeps its neutral value unless a document says otherwise.
    """

    working_required: bool = Field(
        default=False,
        description="True only when a numerical answer with no formula or working written earns "
        "no marks, even if the number is right.",
    )
    part_marks: Literal["unstated", "stated_only", "none", "half", "quarter"] = Field(
        default="unstated",
        description="unstated: nothing is said. stated_only: part marks are given only where the "
        "rubric names them (whole marks otherwise). none: no part marks anywhere. half or "
        "quarter: part marks come in halves or quarters of a point.",
    )
    mark_step: float | None = Field(
        default=None,
        gt=0,
        description="Set only when every mark in the exam is stated to be a multiple of one "
        "number, such as 0.5. Leave empty when whole marks are the usual rule but the rubric "
        "names exceptions.",
    )
    follow_through: bool | None = Field(
        default=None,
        description="True when a later part is marked on the student's own earlier wrong result; "
        "False when the documents forbid it; empty when nothing is said.",
    )
    count_best: int | None = Field(
        default=None,
        ge=1,
        description="How many questions count towards the total when candidates may attempt more "
        "than are needed (the best three of four counts three). Empty when every question counts.",
    )
    notes: list[str] = Field(
        default_factory=list,
        description="Other exam-wide rules that change how a single answer is marked (for "
        "example deductions for missing units, or what to do with a method that differs from "
        "the key). One short sentence each, close to the document's own words.",
    )

    @property
    def found(self) -> bool:
        """Say whether the document gave any rule at all."""
        return self != ExamRules()

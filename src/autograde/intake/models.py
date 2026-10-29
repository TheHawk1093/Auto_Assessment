"""The exam as the teacher gives it: a question paper, reference files, student answers."""

from __future__ import annotations

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
        return round(sum(q.max_mark for q in self.questions), 6)

    @property
    def ids(self) -> list[str]:
        return [q.id for q in self.questions]


class Reference(BaseModel):
    """What the teacher supplied for one question. Either part may be missing."""

    model_answer: str = ""
    rubric: str = ""
    tests: str = ""  # code questions: one assert per line

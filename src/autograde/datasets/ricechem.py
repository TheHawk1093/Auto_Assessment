"""RiceChem: college chemistry short essays graded with a published rubric.

The dataset gives, for each student, the answer, the total score and which rubric criteria were
ticked. It has no model answer and no marks per criterion, so both are rebuilt here:

- The marks per criterion were recovered by fitting the criteria ticks to the scores. For the
  three questions kept here the fit is almost exact (R squared 0.98 to 0.998) and each total is 8.
- The reference answer is the list of criteria written as statements. Every method gets the same
  reference, so the comparison between methods is fair.
- Question 3 is left out: its scoring does not reduce to a clean sum of criteria.

Deductions (a calculation error, an incorrect statement) are kept as a note in the rubric.
The system adds up positive points only, so it cannot subtract them: a small, known gap.
"""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

from autograde.schemas import Item, Rubric, RubricPoint, RubricRecord

DATASET = "ricechem"
FOLDER = "RiceChem Dataset"

# Per question: (marks, criterion column, column for a partial-credit tick or None, extra note)
_Q1 = [
    (1.0, "correctly cites decreased electron electron repulsion", None, ""),
    (1.0, "relates decreased electron electron repulsion to decreased potential energy", None, ""),
    (1.0, "3rd and 4th electrons ionized feel same core charge", None, ""),
    (1.0, "3rd and 4th electrons ionized from n=3 shell and have same radius", None, ""),
    (1.0, "5th electron ionized from n=2 shell and feels higher core charge", None, ""),
    (1.0, "5th electron ionized from n=2 shell and has smaller radius", None, ""),
    (
        2.0,
        "correctly explains relationship of potential energy to ionization energy",
        "partially explains relationship between potential energy and ionization energy",
        "1 of 2 marks if the relationship is only partially explained.",
    ),
]
_Q2 = [
    (2.0, "Correctly states that frequency is proportional to energy of light", None, ""),
    (1.0, "Explaining sentence 1: energy levels of an electron in an atom are quantized", None, ""),
    (
        2.0,
        "Explaining sentence 1: FULLY explains energy/frequency absorbed must equal the "
        "difference in energy levels in an electron",
        "Explaining sentence 1: PARTIALLY explains energy/frequency absorbed must equal the "
        "difference in energy levels in an electron",
        "1 of 2 marks if only partially explained.",
    ),
    (
        1.0,
        "Explaining sentence 2: a minimum amount of energy is needed to eject an electron",
        None,
        "",
    ),
    (2.0, "Explaining sentence 2: any additional energy becomes kinetic energy", None, ""),
]
_Q4 = [
    (1.0, "Fixed mass of one element", None, ""),
    (1.0, "Mass data in LoMP", None, ""),
    (1.0, "Combine to form compounds", None, ""),
    (1.0, "Integer/whole number ratio", None, ""),
    (2.0, "Whole numbers mean indivisible/discrete", None, ""),
    (2.0, "Indivisible unit of mass = atom", None, ""),
]
SPEC = {
    "Q1": (1, _Q1, "Deduct 0.5 for a core charge calculation error."),
    "Q2": (2, _Q2, "Deduct 1 for an incorrect statement."),
    "Q4": (4, _Q4, "Deduct 1 for an incorrect or misleading statement."),
}


def _clean(text: object) -> str:
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    return re.sub(r"[ \t]+", " ", str(text)).strip()


def find_folder(root: Path) -> Path:
    for cand in (root / FOLDER, root.parent / FOLDER, root / DATASET):
        if cand.exists():
            return cand
    raise FileNotFoundError(f"RiceChem folder not found near {root} (looked for '{FOLDER}').")


def official_rubric(qid: str) -> Rubric:
    """The dataset's own criteria as a rubric, with marks recovered from the scores."""
    _, points, deduct = SPEC[qid]
    return Rubric(
        points=[
            RubricPoint(id=f"P{i}", description=desc, marks=marks, partial_credit=partial_note)
            for i, (marks, desc, _, partial_note) in enumerate(points, 1)
        ],
        notes=f"Marked point by point from the published rubric. {deduct}",
    )


def official_record(qid: str) -> RubricRecord:
    return RubricRecord(question_key=f"{DATASET}/{qid}", rubric=official_rubric(qid))


def reference_answer(qid: str) -> str:
    """No model answer exists, so list what a full-mark answer must contain."""
    _, points, _ = SPEC[qid]
    lines = [f"- {desc.split(': ', 1)[-1]} ({marks:g} marks)" for marks, desc, _, _ in points]
    return "A full-mark answer contains all of the following:\n" + "\n".join(lines)


def load_ricechem(root: Path) -> list[Item]:
    folder = find_folder(root)
    items: list[Item] = []
    for qid, (n, points, _) in SPEC.items():
        answers = pd.read_csv(folder / f"Student Answers Q{n}.csv")
        graded = pd.read_csv(folder / f"Graded Rubric Q{n}.csv").set_index("SID")
        question = _clean(answers.columns[1].split(": ", 1)[1])
        reference = reference_answer(qid)
        max_mark = sum(p[0] for p in points)
        for row in answers.itertuples(index=False):
            sid = row[0]
            if sid not in graded.index:
                continue
            g = graded.loc[sid]
            labels = {}
            for i, (_, col, partial_col, _) in enumerate(points, 1):
                if bool(g[col]):
                    labels[f"P{i}"] = "met"
                elif partial_col and bool(g[partial_col]):
                    labels[f"P{i}"] = "partial"
                else:
                    labels[f"P{i}"] = "not_met"
            items.append(
                Item(
                    id=f"{DATASET}/{qid}/{sid}",
                    dataset=DATASET,
                    question_id=qid,
                    question=question,
                    model_answer=reference,
                    student_answer=_clean(row[1]),
                    max_mark=max_mark,
                    human_mark=float(g["Score"]),
                    labels=labels,
                )
            )
    return items

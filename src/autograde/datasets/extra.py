"""Loaders for the sample datasets of other task types (`autograde download --samples`).

Each one turns its raw files into `Item`s. None has a model answer written for it, so where the
data gives no reference the item says so and the marking scheme is built from the question.
They are used for measuring only, so they ignore the dev/test split.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd

from autograde.schemas import NO_REFERENCE, Item

ESSAY_GUIDE = (
    "Holistic essay score from 1 to 6. 6: a clear, well-developed position with strong "
    "reasoning and evidence, well organised, precise language, almost no errors. 5: a clear "
    "position, mostly well developed and organised, few errors. 4: adequate position and "
    "development, some lapses in organisation or language. 3: a position is present but "
    "development is thin or uneven, noticeable errors. 2: weak position and development, "
    "poor organisation, frequent errors. 1: no clear position, very little development, "
    "errors that obstruct meaning."
)
VERIFY_GUIDE = (
    "The solution earns the mark only if every step is mathematically valid and the final "
    "answer is correct. A single wrong step, or a wrong final answer, earns nothing."
)
SCIENTSBANK_MARKS = {"correct": 1.0, "partially_correct_incomplete": 0.5}


def _clean(text: object) -> str:
    return re.sub(r"\s+", " ", str(text)).strip()


def _key(*parts: str) -> str:
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:10]


def load_asap_sas(root: Path) -> list[Item]:
    """ASAP short answers: 10 prompts, scores 0 to 2 or 3 (mean of two graders).

    The prompt holds the question and, for two of the prompts, the rubric after its heading.
    """
    df = pd.read_csv(root / "asap_sas" / "train.csv")
    top = df.groupby("essay_set")["Score1"].max()
    items = []
    for row in df.itertuples(index=False):
        prompt = str(row.prompt).replace("\ufffd", "'")
        cut = prompt.find("Rubric")
        question, reference = (prompt[:cut], prompt[cut:]) if cut > 0 else (prompt, NO_REFERENCE)
        items.append(
            Item(
                id=f"asap_sas/{int(row.Id)}",
                dataset="asap_sas",
                question_id=f"set{int(row.essay_set)}",
                question=_clean(question),
                model_answer=_clean(reference),
                student_answer=_clean(row.essay_text),
                max_mark=float(top[row.essay_set]),
                human_mark=float((row.Score1 + row.Score2) / 2),
            )
        )
    return items


def load_scientsbank(root: Path) -> list[Item]:
    """SemEval-2013 science answers. Five-way label turned into 1, 0.5 or 0 marks."""
    df = pd.read_parquet(root / "scientsbank" / "test.parquet")
    return [
        Item(
            id=f"scientsbank/{row.student_answer_id}",
            dataset="scientsbank",
            question_id=str(row.question_id),
            question=_clean(row.question),
            model_answer=_clean(row.reference_answer),
            student_answer=_clean(row.student_answer),
            max_mark=1.0,
            human_mark=SCIENTSBANK_MARKS.get(row.label_5way, 0.0),
        )
        for row in df.itertuples(index=False)
    ]


def load_aes2(root: Path) -> list[Item]:
    """Persuasive essays with a holistic score from 1 to 6. The prompt each essay answers is
    not in the data, so every essay is judged as an answer to a general persuasive task."""
    df = pd.read_csv(root / "aes2" / "train.csv")
    question = "Write a persuasive essay that takes a clear position and supports it."
    return [
        Item(
            id=f"aes2/{row.essay_id}",
            dataset="aes2",
            question_id="persuasive",
            question=question,
            model_answer=ESSAY_GUIDE,
            student_answer=str(row.full_text).strip(),
            max_mark=6.0,
            kind="essay",
            human_mark=float(row.score),
        )
        for row in df.itertuples(index=False)
    ]


def load_processbench(
    root: Path, parts: tuple[str, ...] = ("gsm8k", "math"), name: str = "processbench"
) -> list[Item]:
    """Maths solutions split into steps; full marks only if no step is wrong."""
    items = []
    for part in parts:
        for row in json.loads((root / "processbench" / f"{part}.json").read_text("utf-8")):
            steps = "\n".join(f"Step {i}: {s}" for i, s in enumerate(row["steps"]))
            items.append(
                Item(
                    id=f"{name}/{part}/{row['id']}",
                    dataset=name,
                    question_id=_key(part, row["problem"]),
                    question=_clean(row["problem"]),
                    model_answer=VERIFY_GUIDE,
                    student_answer=steps,
                    max_mark=1.0,
                    kind="maths",
                    human_mark=1.0 if row["label"] == -1 else 0.0,
                )
            )
    return items


def load_processbench_hard(root: Path) -> list[Item]:
    """The olympiad-level parts of ProcessBench, where wrong steps are subtle."""
    return load_processbench(root, ("olympiadbench", "omnimath"), "processbench_hard")


def load_imo_grading(root: Path) -> list[Item]:
    """Olympiad proofs written by models and graded 0 to 7 by humans. The grading guidelines
    stand in for the teacher's rubric. Among the hardest things to mark."""
    df = pd.read_parquet(root / "imo_grading" / "train.parquet")
    return [
        Item(
            id=f"imo_grading/{row[0]}",
            dataset="imo_grading",
            question_id=str(row[1]),
            question=_clean(row[2]),
            model_answer=_clean(f"Grading guidelines: {row[4]}"),
            student_answer=str(row[3]).strip(),
            max_mark=7.0,
            kind="maths",
            human_mark=float(row[6]),
            human_feedback=_clean(row[5]),
        )
        for row in df.itertuples(index=False)
    ]

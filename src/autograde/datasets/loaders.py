"""Turn each raw dataset into a flat list of `Item`s (one student answer per item)."""

from __future__ import annotations

import hashlib
import random
import re
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path
from typing import Literal

import pandas as pd

from autograde.datasets.extra import (
    load_aes2,
    load_asap_sas,
    load_imo_grading,
    load_processbench,
    load_processbench_hard,
    load_scientsbank,
)
from autograde.datasets.ricechem import load_ricechem
from autograde.schemas import Item

Split = Literal["dev", "test"]


def split_of(question_key: str) -> Split:
    """Assign a question to dev or test. Split by question so no question is in both."""
    digest = hashlib.sha1(question_key.encode("utf-8")).digest()
    return "dev" if digest[0] % 2 == 0 else "test"


def _clean(text: object) -> str:
    return re.sub(r"\s+", " ", str(text).replace("<STOP>", " ")).strip()


def load_digiklausur(root: Path) -> list[Item]:
    """Neural-networks exam. Marks 0, 1, 2. Reference answer per row."""
    df = pd.read_csv(root / "digiklausur" / "asag_dataset.csv")
    return [
        Item(
            id=f"digiklausur/{row.question_id}/{i}",
            dataset="digiklausur",
            question_id=str(row.question_id),
            question=_clean(row.question),
            model_answer=_clean(row.ref_answer),
            student_answer=_clean(row.student_answer),
            max_mark=2.0,
            human_mark=float(row.grades_round),
        )
        for i, row in enumerate(df.itertuples(index=False))
    ]


def load_mohler(root: Path) -> list[Item]:
    """Data-structures course. Marks 0 to 5, mean of two graders."""
    df = pd.read_parquet(root / "mohler" / "cleaned-oe-00001.parquet")
    return [
        Item(
            id=f"mohler/{row.id}",
            dataset="mohler",
            question_id=row.id.rsplit(".", 1)[0],
            question=_clean(row.question),
            model_answer=_clean(row.instructor_answer),
            student_answer=_clean(row.student_answer),
            max_mark=5.0,
            human_mark=float(row.score_avg),
        )
        for row in df.itertuples(index=False)
    ]


def load_saf(root: Path) -> list[Item]:
    """Communication-networks answers with teacher feedback. Marks are 0 to 1."""
    items: list[Item] = []
    for path in sorted((root / "saf" / "data").glob("*/english/*.xml")):
        q = ET.parse(path).getroot()
        qid = f"{q.get('module')}_{q.get('id')}"
        text = _clean(q.findtext("questionText", ""))
        refs = [_clean(r.text or "") for r in q.iter("referenceAnswer")]
        for a in q.iter("studentAnswer"):
            items.append(
                Item(
                    id=f"saf/{a.get('id')}",
                    dataset="saf",
                    question_id=qid,
                    question=text,
                    model_answer=" ".join(refs),
                    student_answer=_clean(a.findtext("response", "")),
                    max_mark=1.0,
                    human_mark=float(a.findtext("score", "0").strip()),
                    human_feedback=_clean(a.findtext("response_feedback", "")) or None,
                )
            )
    return items


def load_engsaf(root: Path) -> list[Item]:
    """Engineering exams from many subjects. Marks 0, 1, 2. Benchmark only: never tuned on.

    A community copy of EngSAF. Its `rationale` text is AI-written, so it is not used as
    teacher feedback. Two reference answers exist for a few questions, so the question id
    is a hash of the question and its reference answer.
    """
    items: list[Item] = []
    for part in ("train", "validation", "test"):
        df = pd.read_csv(root / "engsaf" / f"{part}.csv").fillna("")
        for i, row in enumerate(df.itertuples(index=False)):
            key = hashlib.sha1(f"{row.question}|{row.reference_answer}".encode()).hexdigest()[:10]
            items.append(
                Item(
                    id=f"engsaf/{part}/{i}",
                    dataset="engsaf",
                    question_id=key,
                    question=_clean(row.question),
                    model_answer=_clean(row.reference_answer),
                    student_answer=_clean(row.student_answer),
                    max_mark=2.0,
                    human_mark=float(row.score),
                )
            )
    return items


# Datasets that are only ever used to measure, never to tune. They ignore the dev/test split.
BENCHMARK_ONLY = {
    "engsaf",
    "ricechem",
    "asap_sas",
    "scientsbank",
    "aes2",
    "processbench",
    "imo_grading",
    "processbench_hard",
}

LOADERS: dict[str, Callable[[Path], list[Item]]] = {
    "digiklausur": load_digiklausur,
    "mohler": load_mohler,
    "saf": load_saf,
    "engsaf": load_engsaf,
    "ricechem": load_ricechem,
    "asap_sas": load_asap_sas,
    "scientsbank": load_scientsbank,
    "aes2": load_aes2,
    "processbench": load_processbench,
    "imo_grading": load_imo_grading,
    "processbench_hard": load_processbench_hard,
}


def load_dataset(name: str, data_dir: Path) -> list[Item]:
    if name not in LOADERS:
        raise KeyError(f"Unknown dataset {name!r}. Choose from {sorted(LOADERS)}.")
    return LOADERS[name](data_dir)


def select(items: list[Item], split: Split, n: int | None, seed: int = 0) -> list[Item]:
    """Items from one split, optionally a random sample of size n (reproducible)."""
    pool = [i for i in items if i.dataset in BENCHMARK_ONLY or split_of(i.question_key) == split]
    if n is None or n >= len(pool):
        return pool
    return random.Random(seed).sample(pool, n)

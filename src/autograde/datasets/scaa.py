"""ScAA: children's science answers in Hindi and Marathi, graded correct or incorrect.

Source: github.com/PrathamOrg/ScAA-Dataset (CC BY-NC-SA 4.0, so non-commercial use only). Two
annotators gave each answer a grade, 1 for correct and 2 for incorrect. Only answers on which
both agree are kept, so the label is not an arbitrary pick between two disagreeing graders.
The answers are typed (no handwriting), which makes this a test of marking in an Indic language
alone, separate from reading it.
"""

from __future__ import annotations

from pathlib import Path

from autograde.datasets.xlsx import read_xlsx
from autograde.schemas import Item


def load_scaa(root: Path, language: str) -> list[Item]:
    """Items for one language ("Hindi" or "Marathi"). Marks are 1 (correct) or 0 (incorrect)."""
    rows = read_xlsx(root / "scaa" / "Dataset" / f"{language}.xlsx")
    header = rows[0]
    col = {name: header.index(name) for name in ("Question", "Model Answer", "User Answer")}
    g1, g2 = header.index("Grade1"), header.index("Grade2")
    questions: dict[str, str] = {}
    items = []
    for n, row in enumerate(rows[1:], 1):
        if len(row) <= g2 or row[g1] != row[g2] or row[g1] not in ("1", "2"):
            continue  # missing, or the two annotators disagree
        question = row[col["Question"]].strip()
        qid = questions.setdefault(question, f"q{len(questions) + 1}")
        items.append(
            Item(
                id=f"scaa_{language.lower()}/{n}",
                dataset=f"scaa_{language.lower()}",
                question_id=qid,
                question=question,
                model_answer=row[col["Model Answer"]].strip(),
                student_answer=row[col["User Answer"]].strip(),
                max_mark=1.0,
                human_mark=1.0 if row[g1] == "1" else 0.0,
            )
        )
    return items


def load_scaa_hindi(root: Path) -> list[Item]:
    return load_scaa(root, "Hindi")


def load_scaa_marathi(root: Path) -> list[Item]:
    return load_scaa(root, "Marathi")

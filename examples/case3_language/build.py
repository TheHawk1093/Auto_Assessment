"""Case 3: a language exam with English, Hindi and Marathi questions, built from real data.

Questions and the students' answers come from public datasets (ScAA for Hindi and Marathi, Mohler
for English); the marks are the human graders' marks, so the pipeline can be checked against
people. Nothing is written by hand and nothing is committed: the output goes to the git-ignored
`app_data/case3/` because the datasets' licences (ScAA is CC BY-NC-SA) do not allow redistribution
here. Needs `data/raw/scaa` and `data/raw/mohler`.

    python examples/case3_language/build.py

Writes into app_data/case3/: paper.md, reference.json, roster.csv, answers/<roll>.md (typed, with
a Name / Roll No header), expected_marks.csv (the human marks, as low-high ranges).

Which student answers well is designed, not copied from one real student: for every question the
persona gets a real answer whose human mark matches the pattern below.

| Student | Pattern (English / Hindi / Marathi, share of full marks) |
|---|---|
| S24001 (A) | strong in all three |
| S24002 (B) | strong English, strong Hindi, weak Marathi |
| S24003 (C) | weak English, strong Hindi and Marathi |
| S24004 (D) | strong English only |
| S24005 (E) | strong Hindi only (answers wholly in Hindi) |
| S24006 (F) | weak everywhere |
| S24007 (G) | average everywhere |
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402

from autograde.datasets.xlsx import read_xlsx  # noqa: E402

DATA = ROOT / "data" / "raw"
OUT = ROOT / "app_data" / "case3"
ROLLS = [f"S24{n:03d}" for n in range(1, 8)]
NAMES = {r: f"student_{c}" for r, c in zip(ROLLS, "ABCDEFG", strict=True)}
# per student: share (0 to 1) of full marks wanted for English, Hindi, Marathi answers
PATTERN = {
    "S24001": (1.0, 1.0, 1.0),
    "S24002": (1.0, 1.0, 0.0),
    "S24003": (0.2, 1.0, 1.0),
    "S24004": (1.0, 0.0, 0.0),
    "S24005": (0.4, 1.0, 0.0),
    "S24006": (0.0, 0.0, 0.2),
    "S24007": (0.6, 1.0, 0.0),
}
PER_LANGUAGE = 4  # questions in each language
SEED = 7


HINDI_WORDS = re.compile(r"(?<!\S)(है|हैं|नहीं|और|में|को|लिए|होता|होती|जाता|जाती|कि|यह|वह|था)(?!\S)")
MARATHI_WORDS = re.compile(r"ळ|(?<!\S)(आहे|आहेत|नाही|आणि|होतो|असतो|असते|मध्ये|म्हणून|त्यामुळे|करतो)(?!\S)")
OTHER = {"Hindi": MARATHI_WORDS, "Marathi": HINDI_WORDS}


def in_language(text: str, language: str) -> bool:
    """True when the text is mostly Devanagari and carries no word of the other language."""
    letters = [c for c in text if c.isalpha()]
    if not letters or sum("ऀ" <= c <= "ॿ" for c in letters) / len(letters) < 0.8:
        return False
    return not OTHER[language].search(text)


def clean(text: str) -> str:
    """Remove the dataset's tokenizer marks (<STOP>, -LRB-, -RRB-) and tidy the spaces."""
    text = text.replace("<STOP>", " ").replace("-LRB-", "(").replace("-RRB-", ")")
    return " ".join(text.split())


def english() -> list[dict]:
    """Four Mohler questions with a spread of student answers and their mean human marks."""
    df = pd.read_parquet(DATA / "mohler" / "cleaned-oe-00001.parquet")
    df["q"] = df["id"].str.rsplit(".", n=1).str[0]
    good = [q for q, g in df.groupby("q") if g.score_avg.min() <= 2 and g.score_avg.max() >= 4.5]
    random.Random(SEED).shuffle(good)
    out = []
    for q in sorted(good[:PER_LANGUAGE]):
        g = df[df.q == q]
        out.append(
            {
                "text": clean(g.question.iloc[0]),
                "model": clean(g.instructor_answer.iloc[0]),
                "answers": [(clean(r.student_answer), float(r.score_avg)) for r in g.itertuples()],
                "max": 5.0,
            }
        )
    return out


def indic(language: str) -> list[dict]:
    """Four ScAA questions of the language, with answers both annotators agree on (1 or 0)."""
    rows = read_xlsx(DATA / "scaa" / "Dataset" / f"{language}.xlsx")
    head = rows[0]
    col = {
        n: head.index(n) for n in ("Question", "Model Answer", "User Answer", "Grade1", "Grade2")
    }
    pool: dict[str, dict] = {}
    for r in rows[1:]:
        if len(r) <= col["Grade2"] or r[col["Grade1"]] != r[col["Grade2"]]:
            continue
        if r[col["Grade1"]] not in ("1", "2"):
            continue
        entry = pool.setdefault(
            r[col["Question"]].strip(),
            {"model": r[col["Model Answer"]].strip(), "answers": []},
        )
        answer = r[col["User Answer"]].strip()
        if 3 <= len(answer) <= 200 and in_language(answer, language):
            entry["answers"].append((answer, 1.0 if r[col["Grade1"]] == "1" else 0.0))
    usable = [
        (q, e) for q, e in pool.items()
        if in_language(q, language) and in_language(e["model"], language)
        and sum(m == 1 for _, m in e["answers"]) >= 10 and sum(m == 0 for _, m in e["answers"]) >= 10
    ]  # fmt: skip
    random.Random(SEED).shuffle(usable)
    return [
        {"text": q, "model": e["model"], "answers": e["answers"], "max": 2.0}
        for q, e in sorted(usable[:PER_LANGUAGE])
    ]


def pick(question: dict, share: float, rng: random.Random, used: set[str]) -> tuple[str, float]:
    """A real answer whose human mark (as a share of full marks) is nearest `share`."""
    options = sorted(
        (a for a in question["answers"] if a[0] not in used),
        key=lambda a: (abs(a[1] / question["max"] - share), rng.random()),
    )
    answer, mark = options[0]
    used.add(answer)
    return answer, mark


def main() -> None:
    sections = [("English", english()), ("Hindi", indic("Hindi")), ("Marathi", indic("Marathi"))]
    rng = random.Random(SEED)
    (OUT / "answers").mkdir(parents=True, exist_ok=True)
    paper = [
        "# Language and Science Exam",
        "",
        "Answer every question in the language it is asked in.",
        "",
    ]
    reference: dict[str, dict] = {}
    qid = 0
    numbered: list[tuple[int, int, dict]] = []  # (question id, language index, question)
    for li, (language, questions) in enumerate(sections):
        paper += [f"## Section {li + 1}: {language}", ""]
        for q in questions:
            qid += 1
            marks = int(q["max"])
            paper += [f"### Q{qid}. ({marks} marks)", "", q["text"], ""]
            reference[str(qid)] = {"model_answer": q["model"]}
            numbered.append((qid, li, q))
    (OUT / "paper.md").write_text("\n".join(paper), encoding="utf-8")
    (OUT / "reference.json").write_text(
        json.dumps(reference, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    with (OUT / "roster.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "name", "email"])
        for roll in ROLLS:
            w.writerow([roll, NAMES[roll], f"{NAMES[roll]}@example.edu"])
    expected = [["student", "question", "low", "high", "why"]]
    used: dict[int, set[str]] = {n: set() for n, _, _ in numbered}
    for roll in ROLLS:
        text = [f"Name: {NAMES[roll]}", f"Roll No: {roll}", ""]
        for n, li, q in numbered:
            answer, mark = pick(q, PATTERN[roll][li], rng, used[n])
            text += [f"Q{n}. {answer}", ""]
            full = q["max"]
            low, high = (
                (mark - 1.0, mark + 1.0)
                if full == 5.0
                else ((full / 2, full) if mark else (0.0, full / 2))
            )
            expected.append([roll, str(n), f"{max(low, 0):g}", f"{min(high, full):g}",
                             f"human mark {mark:g} of {full:g}"])  # fmt: skip
        (OUT / "answers" / f"{roll}.md").write_text("\n".join(text), encoding="utf-8")
    with (OUT / "expected_marks.csv").open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(expected)
    print(f"wrote {len(ROLLS)} answer sheets and a {qid}-question paper to {OUT}")


if __name__ == "__main__":
    main()

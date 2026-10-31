"""Case 1: one printed exam with every kind of question, built from real data.

Multiple choice (Mendeley), short answers (DigiKlausur), a long essay (aes2) and two maths proofs
(imo_grading). Questions, reference answers and the students' answers are real; the marks are the
human graders' marks, so the pipeline can be checked against people. The output goes to the
git-ignored `app_data/case1/` because the datasets' licences do not allow redistribution here.
Needs `data/raw/mendeley_exam`, `digiklausur`, `aes2` and `imo_grading`.

    python examples/case1_printed/build.py

Writes into app_data/case1/: paper.md, reference.json, roster.csv, answers/<roll>.md (typed, with
a Name / Roll No header) and expected_marks.csv (the human marks as low-high ranges).

Who is strong where is designed: for every question the persona gets a real answer whose human
mark matches the pattern (share of full marks) below.

| Student | MCQ | short | essay | maths |
|---|---|---|---|---|
| S24001 | 1.0 | 1.0 | 1.0 | 1.0 |
| S24002 | 1.0 | 1.0 | 0.8 | 0.6 |
| S24003 | 0.75 | 0.5 | 0.5 | 0.4 |
| S24004 | 0.5 | 1.0 | 0.3 | 0.0 |
| S24005 | 1.0 | 0.5 | 0.7 | 1.0 |
| S24006 | 0.25 | 0.0 | 0.2 | 0.0 |
| S24007 | 0.75 | 0.5 | 0.5 | 0.9 |
"""

from __future__ import annotations

import csv
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from autograde.datasets.loaders import load_dataset  # noqa: E402

DATA = ROOT / "data" / "raw"
OUT = ROOT / "app_data" / "case1"
ROLLS = [f"S24{n:03d}" for n in range(1, 8)]
NAMES = {r: f"student_{c}" for r, c in zip(ROLLS, "ABCDEFG", strict=True)}
PATTERN = {  # share of full marks wanted: mcq, short, essay, maths
    "S24001": (1.0, 1.0, 1.0, 1.0),
    "S24002": (1.0, 1.0, 0.8, 0.6),
    "S24003": (0.75, 0.5, 0.5, 0.4),
    "S24004": (0.5, 1.0, 0.3, 0.0),
    "S24005": (1.0, 0.5, 0.7, 1.0),
    "S24006": (0.25, 0.0, 0.2, 0.0),
    "S24007": (0.75, 0.5, 0.5, 0.9),
}
SEED = 11
MCQ_QUESTIONS = (1, 5, 8, 13)  # numbers in the Mendeley paper
TOLERANCE = {"mcq": 0.0, "short": 1.0, "essay": 1.0, "maths": 2.0}


def clean(text: str) -> str:
    return " ".join(text.replace("<STOP>", " ").split())


def mendeley_mcq() -> list[dict]:
    """The chosen multiple-choice questions with options, the key and real students' choices."""
    base = DATA / "mendeley_exam"
    text = (base / "Question.txt").read_text(encoding="utf-8")
    key = {r["Question_Number"]: r["Correct_Answer"] for r in csv.DictReader(
        (base / "answerkey.txt").open(encoding="utf-8"))}  # fmt: skip
    choices: dict[int, list[str]] = defaultdict(list)
    with (base / "Student_MCQ.csv").open(encoding="utf-8") as f:
        rows = list(csv.reader(f))
    for row in rows[1:]:
        for q in range(1, 21):
            choices[q].append(row[1 + q].strip().upper())
    out = []
    for n in MCQ_QUESTIONS:
        m = re.search(rf"(?ms)^{n}\.\s+(.*?)\n(A\..*?)(?=\n\n|\Z)", text)
        options = [o.strip() for o in m[2].splitlines() if o.strip()]
        right = key[str(n)]
        out.append(
            {
                "text": f"{m[1].strip()}\n" + "\n".join(options),
                "model": f"{right}. " + next(o[3:] for o in options if o.startswith(right)),
                "right": right,
                "wrong": [c for c in choices[n] if c in "ABCD" and c != right],
                "max": 1.0,
            }
        )
    return out


def grouped(name: str, count: int, spread: int) -> list[dict]:
    """`count` questions of a dataset that have answers across at least `spread` different marks."""
    items = load_dataset(name, DATA)
    by_q: dict[str, list] = defaultdict(list)
    for it in items:
        if it.human_mark is not None and 40 <= len(it.student_answer) <= 6000:
            by_q[it.question_id].append(it)
    ok = [q for q, g in by_q.items() if len({i.human_mark for i in g}) >= spread and len(g) >= 12]
    random.Random(SEED).shuffle(ok)
    return [
        {
            "text": clean(by_q[q][0].question),
            "model": clean(by_q[q][0].model_answer),
            "rubric": by_q[q][0].rubric,
            "answers": [(i.student_answer.strip(), float(i.human_mark)) for i in by_q[q]],
            "max": by_q[q][0].max_mark,
        }
        for q in sorted(ok[:count])
    ]


def olympiad(count: int) -> list[dict]:
    """Proof problems with model-written responses graded 0 to 7 by people (read from the file).

    `load_imo_grading` in the package treats the reference solution as the student's answer, so
    the columns are read here: Problem, Solution (reference), Grading guidelines, Response, Points.
    """
    import pandas as pd

    df = pd.read_parquet(DATA / "imo_grading" / "train.parquet")
    df = df[df["Response"].str.len().between(300, 6000)]
    ok = [q for q, g in df.groupby("Problem ID") if g.Points.nunique() >= 4 and len(g) >= 12]
    random.Random(SEED).shuffle(ok)
    out = []
    for pid in sorted(ok[:count]):
        g = df[df["Problem ID"] == pid]
        out.append(
            {
                "text": clean(g["Problem"].iloc[0]),
                "model": clean(g["Solution"].iloc[0]),
                "rubric": clean(g["Grading guidelines"].iloc[0]),
                "answers": [(r.Response.strip(), float(r.Points)) for r in g.itertuples()],
                "max": 7.0,
            }
        )
    return out


def pick(q: dict, share: float, rng: random.Random, used: set[str]) -> tuple[str, float]:
    """A real answer whose human mark (as a share of full marks) is nearest `share`."""
    best = sorted(
        (a for a in q["answers"] if a[0] not in used),
        key=lambda a: (abs(a[1] / q["max"] - share), rng.random()),
    )[0]
    used.add(best[0])
    return best


def main() -> None:
    rng = random.Random(SEED)
    mcq = mendeley_mcq()
    short = grouped("digiklausur", 4, 3)
    essay = grouped("aes2", 1, 4)
    maths = olympiad(2)
    essay[0]["rubric"] = (
        "Holistic score 1 to 6. A clear position (1 mark); supported with reasons and evidence "
        "(2); organised with an introduction, body and conclusion (1); sentences, vocabulary "
        "and conventions (2)."
    )
    sections = [("A. Multiple choice (1 mark each)", "mcq", mcq),
                ("B. Short answers", "short", short),
                ("C. Essay", "essay", essay),
                ("D. Mathematical proofs", "maths", maths)]  # fmt: skip
    (OUT / "answers").mkdir(parents=True, exist_ok=True)
    paper = ["# Mixed Exam", "", "Answer every question.", ""]
    reference: dict[str, dict] = {}
    numbered: list[tuple[int, str, dict]] = []
    n = 0
    for title, kind, questions in sections:
        paper += [f"## Section {title}", ""]
        for q in questions:
            n += 1
            paper += [
                f"### Q{n}. ({q['max']:g} mark{'s' if q['max'] != 1 else ''})",
                "",
                q["text"],
                "",
            ]
            ref = {"model_answer": q["model"]}
            if q.get("rubric"):
                ref["rubric"] = q["rubric"]
            reference[str(n)] = ref
            numbered.append((n, kind, q))
    (OUT / "paper.md").write_text("\n".join(paper), encoding="utf-8")
    (OUT / "reference.json").write_text(
        json.dumps(reference, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    with (OUT / "roster.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "name", "email"])
        for roll in ROLLS:
            w.writerow([roll, NAMES[roll], f"{NAMES[roll]}@example.edu"])
    kinds = ["mcq", "short", "essay", "maths"]
    used: dict[int, set[str]] = {i: set() for i, _, _ in numbered}
    expected = [["student", "question", "low", "high", "why"]]
    for roll in ROLLS:
        lines = [f"Name: {NAMES[roll]}", f"Roll No: {roll}", ""]
        for i, kind, q in numbered:
            share = PATTERN[roll][kinds.index(kind)]
            if kind == "mcq":
                right = share >= 0.5 or rng.random() < share
                answer = q["right"] if right else rng.choice(q["wrong"])
                mark = 1.0 if right else 0.0
            else:
                answer, mark = pick(q, share, rng, used[i])
            lines += [f"Q{i}. {answer}", ""]
            tol = TOLERANCE[kind]
            expected.append([roll, str(i), f"{max(mark - tol, 0):g}", f"{min(mark + tol, q['max']):g}",
                             f"{kind}: human mark {mark:g} of {q['max']:g}"])  # fmt: skip
        (OUT / "answers" / f"{roll}.md").write_text("\n".join(lines), encoding="utf-8")
    with (OUT / "expected_marks.csv").open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(expected)
    print(f"wrote {len(ROLLS)} answer sheets and a {n}-question paper to {OUT}")


if __name__ == "__main__":
    main()

"""Case 2: how well do the handwriting readers do, and does it change the marks?

Uses the Mendeley Data Science exam (data/raw/mendeley_exam, handwritten scans with the teacher's
marks and the students' real MCQ choices). For each reader and each chosen student it:

1. reads the student's pages into a text document (`autograde.ocr.answersheet`, the same reader the
   app uses), and
2. scores the reading against what is known: the 20 multiple-choice letters the student really
   ticked, which short answers the teacher marked (found, missed, invented) and how many spots
   the reader marked unsure.

With `--mark` it then marks each reader's text with the normal exam pipeline and compares the marks
to the teacher's, so the cost of reading mistakes shows up as marking error.

    python examples/case2_ocr/evaluate.py --students Student_4 Student_5 Student_17
    python examples/case2_ocr/evaluate.py --students Student_4 Student_5 --mark

Output: app_data/case2/<reader>/<student>.md and app_data/case2/report.md (git-ignored).
Free Gemini readers only; the free tier may keep the images (they are from a public dataset).
"""

from __future__ import annotations

import argparse
import csv
import re
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from autograde.ocr.answersheet import read_answer_sheet, unsure_count  # noqa: E402

DATA = ROOT / "data" / "raw" / "mendeley_exam"
OUT = ROOT / "app_data" / "case2"
READERS = {
    "gemini-lite": ("gemini", "gemini-3.5-flash-lite"),
    "gemini-flash": ("gemini", "gemini-3.6-flash"),
}
MCQ = range(1, 21)
SHORT = range(21, 36)


def pages_of(student: str) -> list[Path]:
    """The student's page images in page order."""
    found = sorted(
        (DATA / "pages").glob(f"{student}_p*.jpeg"),
        key=lambda p: int(re.search(r"_p(\d+)", p.name)[1]),
    )
    if not found:
        raise SystemExit(f"no pages for {student} in {DATA / 'pages'}")
    return found


def truth() -> dict[str, dict[str, str]]:
    """The teacher's sheet: per student, the MCQ letters ticked and the marks for 21 to 35."""
    with (DATA / "Teacher_manual_marks_Anonymized.csv").open(encoding="utf-8") as f:
        return {row["Student_ID"]: row for row in csv.DictReader(f)}


def sections(text: str) -> dict[int, str]:
    """Split a reading into {question number: answer text} by its `Q<n>.` headings."""
    parts = re.split(r"(?m)^\s*Q\s*(\d+)\s*[.:)]\s*", text)
    return {int(parts[i]): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def letter(answer: str) -> str:
    """The option letter an MCQ answer shows (first A to D standing alone), or ''."""
    m = re.match(r"\W*([A-Da-d])\b", answer)
    return m[1].upper() if m else ""


def read_all(reader: str, students: list[str]) -> dict[str, dict]:
    """Read each student's sheet with the reader (kept if already read) and time it."""
    provider, model = READERS[reader]
    folder = OUT / reader
    folder.mkdir(parents=True, exist_ok=True)
    paper = (DATA / "Question.txt").read_text(encoding="utf-8")
    info: dict[str, dict] = {}
    for student in students:
        target = folder / f"{student}.md"
        t0 = time.time()
        if target.exists():
            info[student] = {"seconds": None}
            continue
        try:
            text = read_answer_sheet(pages_of(student), provider, model, paper)
        except Exception as exc:  # noqa: BLE001 - one failed sheet is a result, not a crash
            print(f"  {reader} {student}: FAILED {str(exc)[:120]}")
            info[student] = {"seconds": None, "failed": True}
            continue
        target.write_text(text, encoding="utf-8")
        info[student] = {"seconds": round(time.time() - t0, 1)}
        print(f"  {reader} {student}: read in {info[student]['seconds']} s")
    return info


def score_reading(reader: str, students: list[str], info: dict[str, dict]) -> dict:
    """MCQ accuracy against the teacher's sheet, short answers found, unsure spans, speed."""
    sheet = truth()
    right = total = hit = truth_n = missed = extra = unsure = 0
    for student in students:
        path = OUT / reader / f"{student}.md"
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        got = sections(text)
        for q in MCQ:
            want = sheet[student][str(q)].strip().upper()
            total += 1
            right += letter(got.get(q, "")) == want
        answered = {q for q in SHORT if sheet[student][str(q)].strip()}  # the teacher marked it
        found = {q for q in SHORT if got.get(q, "").strip()}
        hit, truth_n = hit + len(found & answered), truth_n + len(answered)
        missed, extra = missed + len(answered - found), extra + len(found - answered)
        unsure += unsure_count(text)
    seconds = [v["seconds"] for v in info.values() if v.get("seconds")]
    return {
        "mcq_accuracy": right / total if total else None,
        "mcq_read": f"{right}/{total}",
        "short_found": f"{hit}/{truth_n}",
        "short_missed": missed,
        "short_invented": extra,
        "unsure_spans": unsure,
        "seconds_per_sheet": round(statistics.mean(seconds), 1) if seconds else None,
        "sheets": sum((OUT / reader / f"{s}.md").exists() for s in students),
    }


def mark_reader(reader: str) -> Path:
    """Mark the reader's text with the exam pipeline (DeepSeek via Goedel) and return marks.csv."""
    name = f"case2_{reader}"
    cmd = [
        sys.executable, "-c", "from autograde.cli import main; main()",
        "--config", str(ROOT / "configs" / "exam.yaml"), "exam",
        "--paper", str(DATA / "Question.txt"), "--reference", str(DATA / "answerkey.txt"),
        "--answers", str(OUT / reader), "--name", name,
    ]  # fmt: skip
    print(f"  marking {reader} ...")
    subprocess.run(cmd, cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return ROOT / "runs" / name / "marks.csv"


def compare_marks(marks_csv: Path, students: list[str]) -> dict:
    """The pipeline's marks on questions 21 to 35 against the teacher's (mean error, agreement)."""
    sheet = truth()
    with marks_csv.open(encoding="utf-8") as f:
        got = {r["student"]: r for r in csv.DictReader(f)}
    errors, close, n = [], 0, 0
    for student in students:
        if student not in got:
            continue
        for q in SHORT:
            teacher = sheet[student][str(q)].strip()
            mine = got[student].get(str(q), "").strip()
            if not teacher or not mine:  # the teacher left it blank (unanswered)
                continue
            err = abs(float(mine) - float(teacher))
            errors.append(err)
            close += err <= 0.5
            n += 1
    return {
        "answers_compared": n,
        "mean_abs_error": round(statistics.mean(errors), 2) if errors else None,
        "within_half_mark": f"{close}/{n}",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--students", nargs="+", default=["Student_4", "Student_5", "Student_17"])
    ap.add_argument("--readers", nargs="+", default=list(READERS), choices=list(READERS))
    ap.add_argument("--mark", action="store_true", help="also mark each reading (uses DeepSeek)")
    args = ap.parse_args()
    rows = {}
    for reader in args.readers:
        print(reader)
        info = read_all(reader, args.students)
        rows[reader] = score_reading(reader, args.students, info)
        if args.mark:
            rows[reader] |= compare_marks(mark_reader(reader), args.students)
    lines = [
        "# Case 2: handwriting readers compared",
        "",
        f"Students: {', '.join(args.students)} (Mendeley Data Science exam, real handwriting).",
        "",
    ]
    keys = list(next(iter(rows.values())))
    lines += ["| reader | " + " | ".join(keys) + " |", "|---|" + "---|" * len(keys)]
    for reader, r in rows.items():
        cells = [
            f"{r[k]:.0%}" if k == "mcq_accuracy" and r[k] is not None else str(r[k]) for k in keys
        ]
        lines.append(f"| {reader} | " + " | ".join(cells) + " |")
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()

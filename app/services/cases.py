"""The four demo cases, set up through the real flow so the rest is done in the app.

    python -m app.services.demo clean         # personas, courses, no exams (once)
    python -m app.services.cases seed case1   # also case2, case3, case4, or all
    python -m app.services.cases check case1  # marks against what each student was designed to earn

- case1 (DS1001): exam with every question type (MCQ, short, essay, maths); PDF files.
- case2 (DS1001): handwritten scans of a real exam, read by an AI reader.
- case3 (LA1001): language exam in English, Hindi and Marathi.
- case4 (CS1001): a coding and report assignment submitted as zips, code run in a sandbox.

Cases 1 to 3 are built from datasets and live in the git-ignored `app_data/` (run their
`examples/caseN_*/build.py` first; case 2 needs only `data/raw/mendeley_exam`). Case 4 is synthetic.
What is left for the demo is the teacher's part: read scans or collect submissions, prepare, mark,
review, publish.
"""

from __future__ import annotations

import csv
import re
import shutil
import sys
from datetime import date, timedelta
from pathlib import Path

from app import config
from app.services import courses, demo, grades, models, storage, students, submissions
from app.services.demo_pdf import pdf_bytes

ROOT = config.ROOT
TEACHER = "teacher_1"
DATA = ROOT / "data" / "raw" / "mendeley_exam"
CASE_DIR = {
    "case1": ROOT / "app_data" / "case1",
    "case2": ROOT / "app_data" / "case2",
    "case3": ROOT / "app_data" / "case3",
    "case4": ROOT / "examples" / "case4_coding",
}
EXAM_ID = {k: f"{k}-demo" for k in CASE_DIR}
TITLE = {
    "case1": "Data Science Exam (typed, PDF files)",
    "case2": "Data Science Exam (handwritten scans)",
    "case3": "Language and Science Test (English, Hindi, Marathi)",
    "case4": "Programming Assignment 1 (code and report)",
}
COURSE = {"case1": "DS1001", "case2": "DS1001", "case3": "LA1001", "case4": "CS1001"}
KIND = {"case4": "assignment"}  # the others are exams
# Mendeley students whose handwritten pages become the personas' sheets in case 2
CASE2_STUDENTS = {"S24001": "Student_4", "S24002": "Student_5", "S24003": "Student_17"}


def _course_id(code: str) -> int:
    for c in courses.list_courses(TEACHER):
        if c["code"] == code:
            return c["id"]
    raise SystemExit(
        f"{TEACHER} has no course {code}: run `python -m app.services.demo clean` first."
    )


def _start(case: str) -> tuple[str, int, Path]:
    """Fresh exam for the case; enrol the roster in its course. Returns (id, course id, folder)."""
    folder = CASE_DIR[case]
    if not (folder / "roster.csv").exists():
        raise SystemExit(
            f"{folder} has no roster.csv: build the case data first (see this module)."
        )
    exam_id = EXAM_ID[case]
    demo.forget_exam(exam_id)  # files, marks, overrides, regrades, hand-ins and messages
    cid = _course_id(COURSE[case])
    with (folder / "roster.csv").open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            students.ensure(row["student_id"], row["name"], row["email"])
            courses.enrol(cid, row["student_id"], TEACHER)
    storage.create_exam(
        TITLE[case], owner=TEACHER, exam_id=exam_id, course_id=cid, kind=KIND.get(case, "exam")
    )
    return exam_id, cid, folder


def _upload(exam_id: str, folder: Path, pdf: bool = False) -> None:
    code = set(config.CODE_EXT)
    paper = (folder / "paper.md").read_bytes()
    named = ("paper.pdf", pdf_bytes(paper.decode("utf-8").replace("#", ""))) if pdf else (
        "paper.md", paper)  # fmt: skip
    storage.save_uploads(exam_id, "paper", [named], True, code)
    ref = [("reference.json", (folder / "reference.json").read_bytes())]
    storage.save_uploads(exam_id, "reference", ref, True, code)


def seed_typed(case: str) -> str:
    """Case 1 or 3: paper, reference and each student's typed answer file, as a teacher uploads.

    Case 1 is handed in as PDF files (paper and every answer sheet), case 3 as text files.
    """
    exam_id, _, folder = _start(case)
    _upload(exam_id, folder, pdf=case == "case1")
    if case == "case1":
        files = [
            (f"{p.stem}.pdf", pdf_bytes(p.read_text(encoding="utf-8")))
            for p in sorted((folder / "answers").glob("*.md"))
        ]
    else:
        files = [(p.name, p.read_bytes()) for p in sorted((folder / "answers").glob("*.md"))]
    files.append(("roster.csv", (folder / "roster.csv").read_bytes()))
    storage.save_uploads(exam_id, "answers", files, False, {".csv"})
    return exam_id


def seed_case2() -> str:
    """Handwritten pages of three real students, as personas (identity from the account)."""
    from app.services import scans

    CASE_DIR["case2"].mkdir(parents=True, exist_ok=True)
    with (CASE_DIR["case2"] / "roster.csv").open("w", encoding="utf-8", newline="") as f:
        out = csv.writer(f)
        out.writerow(["student_id", "name", "email"])
        for roll in CASE2_STUDENTS:
            name = f"student_{'ABC'[int(roll[-1]) - 1]}"
            out.writerow([roll, name, f"{name}@example.edu"])
    exam_id, _, folder = _start("case2")
    storage.save_uploads(
        exam_id, "paper", [("Question.txt", (DATA / "Question.txt").read_bytes())], True, set()
    )
    storage.save_uploads(
        exam_id,
        "reference",
        [("answerkey.txt", (DATA / "answerkey.txt").read_bytes())],
        True,
        set(),
    )
    for roll, source in CASE2_STUDENTS.items():
        pages = sorted(
            (DATA / "pages").glob(f"{source}_p*.jpeg"),
            key=lambda p: int(re.search(r"_p(\d+)", p.name)[1]),
        )
        files = [(f"{roll}_p{i}.jpeg", p.read_bytes()) for i, p in enumerate(pages, 1)]
        scans.add(
            exam_id, files, known={roll: {"student_id": roll, "name": students.name_of(roll)}}
        )
    storage.set_reader(exam_id, models.DEFAULT_READER)
    _case2_expected(folder)
    return exam_id


def _case2_expected(folder: Path) -> None:
    """The teacher's marks for the chosen Mendeley students, as ranges (MCQ exact, short +-1)."""
    key = {
        int(r["Question_Number"]): r["Correct_Answer"]
        for r in csv.DictReader((DATA / "answerkey.txt").open(encoding="utf-8"))
    }
    sheet = {
        r["Student_ID"]: r
        for r in csv.DictReader(
            (DATA / "Teacher_manual_marks_Anonymized.csv").open(encoding="utf-8")
        )
    }
    rows = [["student", "question", "low", "high", "why"]]
    for roll, source in CASE2_STUDENTS.items():
        for q in range(1, 21):
            right = sheet[source][str(q)].strip().upper() == key[q]
            rows.append(
                [roll, str(q), str(int(right)), str(int(right)), "MCQ letter the student ticked"]
            )
        for q in range(21, 36):
            raw = sheet[source][str(q)].strip()
            if raw:  # the teacher left unanswered ones blank
                mark = float(raw)
                rows.append(
                    [
                        roll,
                        str(q),
                        f"{max(mark - 1, 0):g}",
                        f"{min(mark + 1, 2):g}",
                        f"teacher gave {mark:g}",
                    ]
                )
    with (folder / "expected_marks.csv").open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def seed_case4() -> str:
    """Coding and report: open submissions and submit each student's zip as that student."""
    exam_id, _, folder = _start("case4")
    _upload(exam_id, folder)
    storage.update_settings(exam_id, code_exec=True)
    deadline = (date.today() + timedelta(days=30)).isoformat()
    submissions.open_window(
        exam_id,
        deadline,
        "Submit one zip: q1.py, q2.py, q3.py and your report as q4_report.docx or .md.",
        TEACHER,
        formats=["documents", "code", "archives"],
    )
    for archive in sorted((folder / "submissions").glob("*.zip")):
        submissions.submit(exam_id, archive.stem, [(archive.name, archive.read_bytes())])
    submissions.collect(exam_id, TEACHER)  # the work is already in the answer sheets
    return exam_id


SNAPSHOTS = config.APP_DATA / "preseeded"  # a marked case saved by `snapshot`, put back by `seed`


def snapshot(case: str) -> Path:
    """Save the marked case (its run and, for scans, the text read from them) for later seeds."""
    eid = EXAM_ID[case]
    out = SNAPSHOTS / case
    shutil.rmtree(out, ignore_errors=True)
    shutil.copytree(storage.run_path(eid), out / "run")
    texts = sorted(storage.upload_dir(eid, "answers").glob("*.md"))
    if case == "case2":
        (out / "answers").mkdir()
        for p in texts:
            shutil.copy2(p, out / "answers" / p.name)
    return out


def restore(case: str) -> bool:
    """Put a saved marked case back over a fresh seed. Returns whether there was one."""
    out = SNAPSHOTS / case
    if not (out / "run").exists():
        return False
    eid = EXAM_ID[case]
    shutil.rmtree(storage.run_path(eid), ignore_errors=True)
    shutil.copytree(out / "run", storage.run_path(eid))
    if (out / "answers").exists():
        target = storage.upload_dir(eid, "answers")
        target.mkdir(parents=True, exist_ok=True)
        for p in (out / "answers").glob("*.md"):
            shutil.copy2(p, target / p.name)
    return True


def seed(case: str) -> str:
    """Set up one case and return its exam id; a saved marked run is put back if there is one."""
    exam_id = {"case2": seed_case2, "case4": seed_case4}.get(case, lambda: seed_typed(case))()
    restore(case)
    return exam_id


def check(case: str, exam_id: str | None = None) -> list[dict]:
    """Final marks against the designed ranges: one row per (student, question)."""
    marks = grades.final_marks(exam_id or EXAM_ID[case])
    rows = []
    with (CASE_DIR[case] / "expected_marks.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            # the paper may call the question "Q1" where the expected file says "1"
            mine = {re.sub(r"^[Qq]", "", k): v for k, v in marks.get(r["student"], {}).items()}
            got = mine.get(r["question"])
            low, high = float(r["low"]), float(r["high"])
            rows.append(
                {**r, "got": got, "ok": got is not None and low - 0.01 <= got <= high + 0.01}
            )
    return rows


def report(rows: list[dict]) -> str:
    """The comparison as a text table, with the share inside the range at the end."""
    lines = [f"{'student':8} {'q':>3} {'got':>5} {'expected':>9}  ok   why"]
    for r in rows:
        got = "-" if r["got"] is None else f"{r['got']:g}"
        lines.append(
            f"{r['student']:8} {r['question']:>3} {got:>5} {r['low'] + '-' + r['high']:>9}  "
            f"{'yes' if r['ok'] else 'NO ':3}  {r['why']}"
        )
    ok = sum(r["ok"] for r in rows)
    lines.append(f"\n{ok} of {len(rows)} answers inside the designed range")
    return "\n".join(lines)


def main() -> None:
    """Command line: seed a case or check its marks."""
    args = sys.argv[1:]
    cases = list(CASE_DIR)
    if len(args) >= 2 and args[0] == "seed" and (args[1] in cases or args[1] == "all"):
        for case in cases if args[1] == "all" else [args[1]]:
            print(f"{case}: created exam {seed(case)}")
    elif len(args) >= 2 and args[0] == "snapshot" and args[1] in cases:
        print(f"saved {args[1]} to {snapshot(args[1])}")
    elif len(args) >= 2 and args[0] == "check" and args[1] in cases:
        print(report(check(args[1], args[2] if len(args) > 2 else None)))
    else:
        sys.exit(
            "usage: python -m app.services.cases seed case1|case2|case3|case4|all"
            " | check caseN [exam id]"
        )


if __name__ == "__main__":
    main()

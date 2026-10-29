"""Photos of a handwritten exam -> marks, against the teacher's marks (Mendeley Data Science exam).

    python tools/ocr/ocr_exam_eval.py --split tune --source gem=runs/ocr_mendeley_tune \
        --config configs/experiments/ocr/ocr_test.yaml --out runs/ocr_exam_tune

`--source` is the output folder of `autograde ocr` (one `<Student>.sheet.json` per student). The
questions, model answers and marks come from the dataset files, never from the OCR, so only the
student's handwriting goes through the reader. Only students of the chosen split are used; the
sealed benchmark students are not on disk. The pipeline is the graded one, with feedback on.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import statistics
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.config import load_settings
from autograde.llm import build_client
from autograde.ocr.sheets import Sheet
from autograde.pipeline.run import run_items
from autograde.schemas import Item

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data/raw/mendeley_exam"
SHORT = range(21, 36)  # the 15 short-answer questions, 2 marks each
MAX_MARK = 2.0
log = logging.getLogger("ocr_exam_eval")


def questions() -> dict[int, str]:
    text = (DATA / "Question.txt").read_text(encoding="utf-8")
    part2 = text.split("Part II", 1)[1]
    return {int(n): q.strip() for n, q in re.findall(r"^(\d+)\.\s+(.+)$", part2, re.M)}


def model_answers() -> dict[int, str]:
    with (DATA / "answerkey.txt").open(encoding="utf-8-sig") as f:
        return {int(r["Question_Number"]): r["Correct_Answer"] for r in csv.DictReader(f)}


def teacher_marks(students: list[str]) -> dict[str, dict[int, float]]:
    """Blank cells and `NM` are left out: no mark was recorded, so there is nothing to compare.
    `NC` (question left blank, no marks given) counts as 0."""
    out: dict[str, dict[int, float]] = {}
    with (DATA / "Teacher_manual_marks_Anonymized.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["Student_ID"] not in students:
                continue
            marks = {}
            for q in SHORT:
                cell = row[str(q)].strip()
                if cell == "NC":
                    marks[q] = 0.0
                elif cell and cell != "NM":
                    marks[q] = float(cell)
            out[row["Student_ID"]] = marks
    return out


def sheet_text(folder: Path, student: str) -> str:
    """Everything the reader produced for the student's pages, in page order. Students number
    their answers in their own way (21, 1, 2.1, ...), so the labels are kept only as hints."""
    paths = sorted(
        folder.glob(f"{student}_p*.sheet.json"),
        key=lambda p: int(re.search(r"_p(\d+)\.sheet", p.name).group(1)),
    ) or [folder / f"{student}.sheet.json"]
    parts = []
    for path in paths:
        if path.exists():
            for it in Sheet.model_validate_json(path.read_text("utf-8")).items:
                if it.student_answer.strip():
                    parts.append(f"{it.question_id}: {it.student_answer}")
    return "\n".join(parts)


class Assigned(BaseModel):
    class Entry(BaseModel):
        id: str
        text: str

    answers: list[Entry]


def assign(client, text: str) -> dict[int, str]:
    """Match the sheet's text to the 15 short-answer questions by content, not by number."""
    qs = questions()
    listed = "\n".join(f"[{q}] {qs[q]}" for q in SHORT)
    user = f"Questions:\n{listed}\n\nOCR text of the sheet:\n{text}"
    got = client.ask(prompts.system("ocr.assign"), user, Assigned)
    found = {e.id.strip("[] Q"): e.text for e in got.answers}
    return {q: found.get(str(q), "") for q in SHORT}


def build_items(
    source: str, assigned: dict[str, dict[int, str]], marks: dict[str, dict[int, float]]
) -> list[Item]:
    qs, keys = questions(), model_answers()
    items = []
    for student, scored in marks.items():
        answers = assigned[student]
        for q in scored:
            items.append(
                Item(
                    id=f"{source}:{student}-Q{q}",
                    dataset="mendeley_exam",
                    question_id=f"Q{q}",  # one scheme per question, shared by all students
                    question=qs[q],
                    model_answer=keys[q],
                    student_answer=answers.get(q, ""),
                    max_mark=MAX_MARK,
                    human_mark=scored[q],
                )
            )
    return items


def summarise(results) -> dict:
    graded = [r for r in results if r.item.human_mark is not None]
    err = [r.predicted_mark - r.item.human_mark for r in graded]
    same = sum(abs(e) < 0.26 for e in err) / len(err)
    out = {
        "n": len(graded),
        "mae_share": round(sum(abs(e) for e in err) / len(err) / MAX_MARK, 3),
        "bias_marks": round(sum(err) / len(err), 3),
        "same_mark": round(same, 3),
        "blank_answers": sum(not r.item.student_answer.strip() for r in graded),
        "with_feedback": sum(r.feedback is not None for r in graded),
    }
    if len({r.item.human_mark for r in graded}) > 1 and len({r.predicted_mark for r in graded}) > 1:
        out["pearson"] = round(
            statistics.correlation(
                [r.item.human_mark for r in graded], [r.predicted_mark for r in graded]
            ),
            3,
        )
    return out


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--split", choices=["tune", "validate"], required=True)
    p.add_argument("--source", action="append", default=[], metavar="NAME=FOLDER")
    p.add_argument("--config", default=str(ROOT / "configs/experiments/ocr/ocr_test.yaml"))
    p.add_argument("--out", required=True)
    a = p.parse_args()
    logging.basicConfig(level=logging.WARNING)

    split = json.loads((DATA / "split.json").read_text("utf-8"))
    marks = teacher_marks(split[a.split])
    settings = load_settings(Path(a.config))
    out = ROOT / a.out
    settings.paths.rubrics_dir = out / "rubrics"
    client = build_client(settings.llm)
    summary = {}
    for spec in a.source:
        name, folder = spec.split("=", 1)
        cache = out / f"assigned_{name}.json"
        done = json.loads(cache.read_text("utf-8")) if cache.exists() else {}
        for student in marks:
            if student not in done:
                text = sheet_text(ROOT / folder, student)
                done[student] = assign(client, text) if text else {q: "" for q in SHORT}
                out.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(done, ensure_ascii=False, indent=1), "utf-8")
        assigned = {s: {int(q): t for q, t in d.items()} for s, d in done.items()}
        items = build_items(name, assigned, marks)
        res = run_items(items, "pipeline", client, settings, out / f"{name}.jsonl")
        summary[name] = summarise(res)
        print(name, json.dumps(summary[name]))
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1), "utf-8")
    print(f"split={a.split} students={len(marks)} cost: grading ${client.usage.cost_usd:.3f}")


if __name__ == "__main__":
    main()

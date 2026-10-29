"""EDU-CIRCUIT-HW: handwritten circuit-analysis solutions with the teaching assistants' deductions.

Source: Georgia Tech, Spring 2025 (code Apache-2.0). Each page is one student's solution to one
textbook problem, worth 1.0; the TA label lists what was deducted, by criterion code. The mark is
1.0 minus those deductions, shown here out of 100 so that a deduction of 0.02 is 2 marks. The
problem texts are withheld by the authors, so the question is known only by its id and the
teacher's rubric (criteria and deduction rules) is the whole reference: this is the "rubric but
no model answer" path, read from handwriting.

Only students of the tune and validate splits are used (`split.json`); the sealed benchmark
students are never loaded here. Pages are transcribed once by a hosted vision model and the text
is kept next to the images (`transcripts/`), so marking runs on text and never repeats the
reading. Run `python -m autograde.datasets.circuit -n 30 --config
configs/experiments/circuit/circuit_gemini.yaml`.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
from pathlib import Path

from autograde import prompts
from autograde.schemas import Item

log = logging.getLogger(__name__)
USED = ("tune", "validate")
SCALE = 100  # the TA's deductions are 0.01 to 0.06 of one mark; on 100 marks they are 1 to 6


def _root(data_dir: Path) -> Path:
    return data_dir / "circuit_hw"


def render_rubric(path: Path) -> str:
    """The rubric file as text for the scheme writer: criteria and the deduction for each error."""
    data = json.loads(path.read_text(encoding="utf-8"))
    lines = [
        f"Worth {SCALE} marks. The student starts with full marks and loses the amounts below "
        "for each error found. Mistakes not listed lose the typical deduction of the matching "
        "criterion."
    ]
    for c in data.get("criteria", []):
        lines.append(
            f"- {c['name']} ({c['code']}): {c['description']} "
            f"Typical deduction {c.get('typical_deduction', 0) * SCALE:g}, at most "
            f"{c.get('max_deduction', 0) * SCALE:g}."
        )
        for rule in c.get("deduction_rules", []):
            lines.append(f"    {rule['id']}: {rule['when']} (lose {rule['deduct'] * SCALE:g})")
    return "\n".join(lines)


def _students(root: Path) -> set[str]:
    split = json.loads((root / "split.json").read_text(encoding="utf-8"))
    return {s for part in USED for s in split[part]}


def page_path(root: Path, homework: str, student: str, qid: str) -> Path:
    return root / homework / student / f"{qid.replace('_', '.')}.png"


def transcript_path(root: Path, homework: str, student: str, qid: str) -> Path:
    return root / "transcripts" / f"{homework}_{student}_{qid}.txt"


def load_circuit_hw(data_dir: Path, pending: bool = False) -> list[Item]:
    """Items with a transcript. With `pending`, also the pages not read yet (to read them)."""
    root = _root(data_dir)
    allowed = _students(root)
    items = []
    with (root / "manually_checked_TA_label" / "valset1.csv").open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            student, hw, qid = row["Student ID"], row["Homework ID"], row["Question ID"]
            rubric = root / "rubric_outputs" / f"P{qid.replace('_', '.')}.json"
            image = page_path(root, hw, student, qid)
            if student not in allowed or not image.exists() or not rubric.exists():
                continue
            deducted = sum(json.loads(row["gt_per_code"] or "{}").values())
            said = transcript_path(root, hw, student, qid)
            if not said.exists() and not pending:
                continue  # not read yet: marking an empty answer would only measure the gap
            items.append(
                Item(
                    id=f"circuit_hw/{hw}/{student}/{qid}",
                    dataset="circuit_hw",
                    question_id=f"P{qid.replace('_', '.')}",
                    question=(
                        f"Circuit analysis, textbook problem {qid.replace('_', '.')} "
                        "(the problem text is not available; mark against the rubric)."
                    ),
                    model_answer="",
                    rubric=render_rubric(rubric),
                    student_answer=said.read_text(encoding="utf-8") if said.exists() else "",
                    max_mark=float(SCALE),
                    kind="maths",
                    field="circuit analysis",
                    human_mark=round(max(0.0, 1.0 - deducted) * SCALE, 2),
                    labels={"image": str(image), "ta_deduction": row["deduction_reason"][:300]},
                )
            )
    return items


def transcribe(items: list[Item], describer, data_dir: Path) -> int:
    """Read each page that has no transcript yet; returns how many were read."""
    root, done = _root(data_dir), 0
    system = prompts.system("circuit.transcribe")
    for item in items:
        _, hw, student, qid = item.id.split("/")
        out = transcript_path(root, hw, student, qid)
        if out.exists():
            continue
        try:
            text = describer([Path(item.labels["image"])], system, "Transcribe this page.")
        except Exception as exc:  # a quota or network failure must not lose the pages done so far
            log.warning("stopped at %s: %s", item.id, exc)
            break
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(re.sub(r"\n{3,}", "\n\n", text).strip(), encoding="utf-8")
        done += 1
    return done


def main() -> None:
    from autograde.config import load_settings
    from autograde.pipeline.figure import make_describer

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", type=Path, default=Path("configs/experiments/indic/gemini_en.yaml"))
    ap.add_argument("-n", type=int, default=30, help="pages to read this time")
    args = ap.parse_args()
    settings = load_settings(args.config)
    from autograde.datasets.loaders import select

    every = load_circuit_hw(settings.paths.data_dir, pending=True)
    items = [i for i in select(every, "dev", None) if not i.student_answer][: args.n]
    print(f"read {transcribe(items, make_describer(settings), settings.paths.data_dir)} pages")


if __name__ == "__main__":
    main()

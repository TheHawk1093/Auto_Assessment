"""Test data for the web app: a finished marking run, as `autograde exam` would leave it."""

from __future__ import annotations

import json

from app.services import storage
from autograde.schemas import Feedback, Item, Result

QUESTIONS = [
    {"id": "1", "text": "Solve $x^2=4$", "max_mark": 2.0, "kind": "short"},
    {"id": "2", "text": "Name the unit of force", "max_mark": 3.0, "kind": "short"},
]
ANSWERS = {  # (student, question) -> (answer, model mark)
    ("S1", "1"): ("उत्तर: \\(x = 2\\) <script>alert(1)</script>", 1.0),
    ("S1", "2"): ("newton", 2.0),
    ("S2", "1"): ("SECRET-S2 x = 2 or -2", 2.0),
    ("S2", "2"): ("newton", 3.0),
}


def fabricate_run(exam_id: str) -> None:
    """Two students, two questions; S2's first answer holds a marker nobody else may see."""
    run = storage.run_path(exam_id)
    (run / "students").mkdir(parents=True)
    info = {
        "paper": {"questions": QUESTIONS},
        "students": ["S1", "S2"],
        "rules": {},
        "warnings": [],
    }
    (run / "intake.json").write_text(json.dumps(info), encoding="utf-8")
    (run / "marks.csv").write_text("student,1,2,total\nS1,1,2,3\nS2,2,3,5\n", encoding="utf-8")
    (run / "schemes.md").write_text("## Question 1\n\\(x=\\pm 2\\)", encoding="utf-8")
    lines = []
    for q in QUESTIONS:
        for student in ("S1", "S2"):
            answer, mark = ANSWERS[(student, q["id"])]
            item = Item(
                id=f"exam/{student}/{q['id']}", dataset="exam", question_id=q["id"],
                question=q["text"], model_answer="MODEL-ANSWER", student_answer=answer,
                max_mark=q["max_mark"],
            )  # fmt: skip
            fb = Feedback(strengths=["good"], improvements=[], summary=f"note for {student}")
            flags = ["retried"] if (student, q["id"]) == ("S1", "1") else []
            r = Result(item=item, mode="pipeline", predicted_mark=mark, feedback=fb, flags=flags)
            lines.append(r.model_dump_json())
    (run / "results.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")

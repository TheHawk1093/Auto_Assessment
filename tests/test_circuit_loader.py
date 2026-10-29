import json

from autograde.datasets.circuit import load_circuit_hw, transcript_path


def build(tmp_path):
    root = tmp_path / "circuit_hw"
    (root / "Homework1" / "student_1").mkdir(parents=True)
    (root / "Homework1" / "student_9").mkdir(parents=True)
    (root / "manually_checked_TA_label").mkdir()
    (root / "rubric_outputs").mkdir()
    for s in ("student_1", "student_9"):
        (root / "Homework1" / s / "1.5-2.png").write_bytes(b"x")
    (root / "split.json").write_text(
        json.dumps({"tune": ["student_1"], "validate": [], "benchmark": ["student_9"]})
    )
    rubric = {
        "criteria": [
            {
                "code": "M", "name": "Method", "description": "Right approach.",
                "typical_deduction": 0.02, "max_deduction": 0.06,
                "deduction_rules": [{"id": "M1", "when": "Divides by time", "deduct": 0.02}],
            }
        ]
    }  # fmt: skip
    (root / "rubric_outputs" / "P1.5-2.json").write_text(json.dumps(rubric))
    rows = [
        "Homework ID,Student ID,Question ID,gt_per_code,deduction_reason",
        'Homework1,student_1,1_5-2,"{""M"": 0.02, ""U"": 0.01}",why',
        "Homework1,student_9,1_5-2,{},none",
    ]
    (root / "manually_checked_TA_label" / "valset1.csv").write_text("\n".join(rows))
    return root


def test_marks_are_100_minus_deductions_and_sealed_students_are_left_out(tmp_path):
    root = build(tmp_path)
    items = load_circuit_hw(tmp_path, pending=True)
    assert [i.id for i in items] == ["circuit_hw/Homework1/student_1/1_5-2"]
    item = items[0]
    assert item.max_mark == 100 and item.human_mark == 97
    assert "lose 2" in item.rubric and item.student_answer == ""
    transcript_path(root, "Homework1", "student_1", "1_5-2").parent.mkdir()
    transcript_path(root, "Homework1", "student_1", "1_5-2").write_text("V = I R")
    assert load_circuit_hw(tmp_path)[0].student_answer == "V = I R"

import json

from autograde.evaluation.judge_check import (
    CRITERIA,
    agreement,
    cohen_kappa,
    export_sheet,
    write_sheet,
)


def test_kappa_is_one_for_identical_and_zero_for_chance():
    assert cohen_kappa([(True, True), (False, False), (True, True)]) == 1.0
    assert cohen_kappa([(True, True), (True, False), (False, True), (False, False)]) == 0.0
    assert cohen_kappa([]) is None


def test_sheet_roundtrip_and_agreement(tmp_path):
    run = tmp_path / "r1"
    run.mkdir()
    item = {"id": "a", "question": "q", "model_answer": "m", "student_answer": "s", "max_mark": 5}
    fb = {"strengths": [], "improvements": [], "summary": "ठीक"}
    (run / "results.jsonl").write_text(
        json.dumps({"item": item, "predicted_mark": 2.0, "feedback": fb}) + "\n", encoding="utf-8"
    )
    judged = {"id": "a", **{c: True for c in CRITERIA}, "actionable": False}
    (run / "feedback_judgements.jsonl").write_text(json.dumps(judged) + "\n", encoding="utf-8")
    rows = export_sheet(tmp_path, ["r1"], per_run=5)
    assert len(rows) == 1 and rows[0]["actionable"] == "n" and rows[0]["anchored"] == "y"
    for c in CRITERIA:
        rows[0]["human_" + c] = "y"
    sheet = tmp_path / "sheet.csv"
    write_sheet(rows, sheet)
    out = agreement(sheet)
    assert out["anchored"]["agree"] == 1.0 and out["actionable"]["agree"] == 0.0

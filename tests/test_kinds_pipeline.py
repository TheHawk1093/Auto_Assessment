"""The teacher's controls and the question kinds, through the whole pipeline with a fake model."""

from pathlib import Path

from autograde.config import PathsConfig, PipelineConfig, Settings, TeacherInputs
from autograde.pipeline.run import run_items
from autograde.schemas import Feedback, Grading, Item, Reading, RubricDraft
from fakes import FakeClient

READING = {"gist": "g", "ideas": [], "problems": []}
FEEDBACK = {"strengths": [], "improvements": [], "summary": "Overall, ok."}


def settings(tmp_path: Path, variant="generated", **teacher) -> Settings:
    return Settings(
        pipeline=PipelineConfig(
            rubric_selftest=False,
            max_workers=1,
            rubric_variant=variant,
            teacher=TeacherInputs(**teacher),
        ),
        paths=PathsConfig(rubrics_dir=tmp_path / "cache", runs_dir=tmp_path / "runs"),
    )


def item(answer: str, kind="short", marks=2.0, question="Explain it.", model="It is x.", **more):
    return Item(
        id="t/1", dataset="t", question_id="q1", question=question, model_answer=model,
        student_answer=answer, max_mark=marks, kind=kind, **more,
    )  # fmt: skip


def client(points: list[dict], status="partial", awarded=1.0):
    def grade(_user: str) -> dict:
        return {"verdicts": [
            {"point_id": p["id"], "status": status, "marks_awarded": awarded,
             "evidence": "it is x", "reason": "r"} for p in points
        ]}  # fmt: skip

    return FakeClient(
        {
            RubricDraft: lambda _u: {"points": points},
            Grading: grade,
            Feedback: lambda _u: FEEDBACK,
            Reading: lambda _u: READING,
        }
    )


ONE_POINT = [{"id": "P1", "description": "says x", "marks": 2.0}]


def mark(tmp_path, it, c, variant="generated", **teacher):
    cfg = settings(tmp_path, variant, **teacher)
    (res,) = run_items([it], "pipeline", c, cfg, tmp_path / "r.jsonl")
    return res


def test_a_half_mark_step_allows_one_and_a_half_out_of_two(tmp_path):
    res = mark(tmp_path, item("it is x"), client(ONE_POINT, awarded=1.7), mark_step=0.5)
    assert res.predicted_mark == 1.5


def test_a_step_of_point_two_allows_one_point_eight(tmp_path):
    res = mark(tmp_path, item("it is x"), client(ONE_POINT, awarded=1.7), mark_step=0.2)
    assert res.predicted_mark == 1.8


def test_a_partial_verdict_never_rounds_up_to_full_marks(tmp_path):
    res = mark(tmp_path, item("it is x"), client(ONE_POINT, awarded=1.95), mark_step=0.2)
    assert res.predicted_mark == 1.8 and res.grading.verdicts[0].status == "partial"


def test_the_grader_is_told_the_step_and_the_scheme_writer_too(tmp_path):
    c = client(ONE_POINT, awarded=1.0)
    mark(tmp_path, item("it is x"), c, variant="solid", mark_step=0.25)
    assert any("steps of 0.25" in u for m, u in c.calls if m is RubricDraft)


def test_teacher_notes_reach_the_marker_and_the_feedback_writer(tmp_path):
    c = client(ONE_POINT, awarded=1.0)
    mark(tmp_path, item("it is x"), c, notes="Units are required.")
    assert any("Units are required." in u for m, u in c.calls if m is Grading)
    assert any("Units are required." in u for m, u in c.calls if m is Feedback)


def test_a_note_for_one_question_does_not_leak_to_another(tmp_path):
    c = client(ONE_POINT, awarded=1.0)
    mark(tmp_path, item("it is x"), c, question_notes={"t/other": "Only for another question."})
    assert not any("Only for another" in u for m, u in c.calls)


NUMERIC_POINTS = [
    {"id": "P1", "description": "final answer", "marks": 2.0,
     "numeric": {"value": 10, "unit": "N", "rel_tol": 0.01, "unit_share": 0.25}},
]  # fmt: skip


def test_code_decides_the_numeric_point_even_if_the_model_credits_a_wrong_number(tmp_path):
    c = client(NUMERIC_POINTS, status="met", awarded=2.0)
    res = mark(tmp_path, item("F = 12 N", kind="numeric"), c)
    assert res.predicted_mark == 0
    grading_prompt = next(u for m, u in c.calls if m is Grading)
    assert "Automatic checks" in grading_prompt and "do not match" in grading_prompt


def test_a_forgotten_unit_costs_only_the_unit_share(tmp_path):
    res = mark(tmp_path, item("F = 10", kind="numeric"), client(NUMERIC_POINTS, "not_met", 0.0))
    assert res.predicted_mark == 1.5 and "unit_missing:P1" in res.flags


def test_a_correct_answer_in_another_unit_gets_full_marks(tmp_path):
    res = mark(
        tmp_path, item("F = 0.01 kN", kind="numeric"), client(NUMERIC_POINTS, "not_met", 0.0)
    )
    assert res.predicted_mark == 2.0 and not res.feedback.improvements


MCQ = "Which is a tree ensemble?\nA. SVM\nB. Random Forest\nC. KNN\nD. Logistic Regression"


def test_a_right_choice_is_marked_with_no_model_call_at_all(tmp_path):
    c = client(ONE_POINT)
    res = mark(tmp_path, item("(b)", kind="mcq", marks=1.0, question=MCQ, model="B"), c)
    assert res.predicted_mark == 1.0
    assert c.count(Grading) == c.count(Reading) == c.count(RubricDraft) == 0


def test_a_wrong_choice_gets_an_explanation_from_the_model(tmp_path):
    c = client(ONE_POINT)
    res = mark(tmp_path, item("C", kind="mcq", marks=1.0, question=MCQ, model="B"), c)
    assert res.predicted_mark == 0 and res.feedback is not None
    prompt = next(u for m, u in c.calls if m is Feedback)
    assert "the correct choice is B" in prompt and "Chose C" in prompt
    assert c.count(Grading) == 0


def test_an_unreadable_choice_is_flagged_and_needs_no_model(tmp_path):
    c = client(ONE_POINT)
    res = mark(tmp_path, item("hmm", kind="mcq", marks=1.0, question=MCQ, model="B"), c)
    assert res.predicted_mark == 0 and "unclear_choice" in res.flags
    assert c.count(Feedback) == 0 and res.feedback.improvements


def test_code_answers_get_a_syntax_fact_for_the_marker(tmp_path):
    c = client(ONE_POINT, awarded=1.0)
    broken = "```python\ndef f(x)\n    return x\n```"
    res = mark(tmp_path, item(broken, kind="code", question="Write a Python function f."), c)
    prompt = next(u for m, u in c.calls if m is Grading)
    assert "syntax error at line" in prompt and "reading mistake" in prompt
    assert "code_syntax_error" in res.flags


def test_a_drawing_without_a_vision_reader_is_not_credited_and_is_flagged(tmp_path, monkeypatch):
    monkeypatch.setattr("autograde.pipeline.run.make_describer", lambda _settings: None)
    c = client(ONE_POINT, awarded=1.0)
    res = mark(tmp_path, item("see figure", kind="diagram", figures=["x.png"]), c)
    prompt = next(u for m, u in c.calls if m is Grading)
    assert "Do not give credit" in prompt and "figure_not_checked" in res.flags


def test_a_missing_image_file_is_flagged_not_a_crash(tmp_path):
    c = client(ONE_POINT, awarded=1.0)
    res = mark(
        tmp_path, item("see figure", kind="diagram", figures=[str(tmp_path / "none.png")]), c
    )
    assert "figure_not_checked" in res.flags and res.predicted_mark >= 0


def test_the_feedback_writer_is_given_the_unit_fact_checked_by_code(tmp_path):
    c = client(NUMERIC_POINTS, "met", 2.0)
    mark(tmp_path, item("F = 12 N", kind="numeric"), c, notes="Units are required.")
    prompt = next(u for m, u in c.calls if m is Feedback)
    assert "Facts checked by code" in prompt and "its unit is right" in prompt


def test_feedback_in_another_language_asks_for_the_fixed_phrases_to_be_translated(tmp_path):
    c = client(ONE_POINT, awarded=1.0)
    cfg = settings(tmp_path)
    cfg.pipeline.feedback_language = "Hindi"
    run_items([item("it is x")], "pipeline", c, cfg, tmp_path / "hi.jsonl")
    prompt = next(u for m, u in c.calls if m is Feedback)
    assert "in Hindi" in prompt and "translated naturally" in prompt

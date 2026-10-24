from pathlib import Path

from autograde.config import PathsConfig, PipelineConfig, Settings
from autograde.pipeline.rubric import build_record
from autograde.pipeline.run import read_results, run_items
from autograde.schemas import Feedback, Grading, Item, Question, Reading, Rubric
from fakes import FakeClient

MODEL_ANSWER = "Gradient descent updates weights against the gradient."


def make_item(i: int, answer: str) -> Item:
    return Item(id=f"t/{i}", dataset="t", question_id="q1", question="What is gradient descent?",
                model_answer=MODEL_ANSWER, student_answer=answer, max_mark=2.0,
                human_mark=1.0)  # fmt: skip


def rubric_handler(_user: str) -> dict:
    return {"points": [
        {"id": "P1", "description": "updates weights", "marks": 1.0},
        {"id": "P2", "description": "uses the gradient", "marks": 1.0},
    ]}  # fmt: skip


def verdicts(p1: bool, p2: bool, quote: str) -> dict:
    def v(pid, ok):
        return {"point_id": pid, "status": "met" if ok else "not_met",
                "marks_awarded": 1.0 if ok else 0.0, "evidence": quote if ok else "",
                "reason": "r"}  # fmt: skip

    return {"verdicts": [v("P1", p1), v("P2", p2)]}


def grade_handler(user: str) -> dict:
    answer = user.split("Student answer:\n")[1].split("\n")[0]
    return verdicts("weights" in answer, "gradient" in answer, answer)


READING = {"gist": "It describes updating weights.", "ideas": ["updates weights"], "problems": []}
FEEDBACK = {"strengths": ["You said it updates weights."], "improvements": [], "summary": "ok"}


def settings(tmp_path: Path) -> Settings:
    return Settings(
        pipeline=PipelineConfig(rubric_selftest=True, max_workers=2),
        paths=PathsConfig(rubrics_dir=tmp_path / "cache", runs_dir=tmp_path / "runs"),
    )


def client() -> FakeClient:
    return FakeClient(
        {
            Rubric: rubric_handler,
            Grading: grade_handler,
            Feedback: lambda _u: FEEDBACK,
            Reading: lambda _u: READING,
        }
    )


def test_end_to_end_marks_come_from_code_and_schemes_are_cached(tmp_path: Path):
    c = client()
    items = [make_item(1, "It updates weights."), make_item(2, "It uses the gradient to move.")]
    out = tmp_path / "res.jsonl"
    results = run_items(items, "pipeline", c, settings(tmp_path), out)
    by_id = {r.item.id: r for r in results}
    assert by_id["t/1"].predicted_mark == 1.0 and by_id["t/2"].predicted_mark == 1.0
    assert all(r.feedback and r.grading for r in results)
    assert c.count(Rubric) == 1  # one scheme for the one question
    # self-test: model answer + a "don't know" answer, plus the two students
    assert c.count(Grading) == 4
    assert c.count(Feedback) == 2
    assert c.count(Reading) == 2  # one reading per student, none for the self-test
    assert all(r.reading for r in results)


def test_reading_reaches_the_marking_prompt_only_when_enabled(tmp_path: Path):
    on, off = client(), client()
    item = [make_item(1, "It updates weights.")]
    run_items(item, "pipeline", on, settings(tmp_path), tmp_path / "a.jsonl")
    cfg = settings(tmp_path)
    cfg.pipeline.read_first = False
    run_items(item, "pipeline", off, cfg, tmp_path / "b.jsonl")
    assert any("first reader" in u for m, u in on.calls if m is Grading)
    assert not any("first reader" in u for m, u in off.calls if m is Grading)
    assert off.count(Reading) == 0


def test_resume_skips_finished_items(tmp_path: Path):
    items = [make_item(1, "It updates weights.")]
    out = tmp_path / "res.jsonl"
    c1 = client()
    run_items(items, "pipeline", c1, settings(tmp_path), out)
    c2 = client()
    results = run_items([*items, make_item(2, "weights")], "pipeline", c2, settings(tmp_path), out)
    assert len(results) == 2 and len(read_results(out)) == 2
    assert c2.count(Rubric) == 0  # cached from the first run
    assert c2.count(Feedback) == 1


def test_empty_answer_costs_no_marking_call(tmp_path: Path):
    c = client()
    results = run_items([make_item(1, "  ")], "pipeline", c, settings(tmp_path),
                        tmp_path / "res.jsonl")  # fmt: skip
    assert results[0].predicted_mark == 0 and "empty_answer" in results[0].flags
    assert c.count(Grading) == 2  # self-test only


def test_bad_marking_is_retried_then_accepted(tmp_path: Path):
    calls = {"n": 0}

    def flaky(user: str) -> dict:
        if "Student answer:\nIt updates weights." in user:
            calls["n"] += 1
            if calls["n"] == 1:
                return verdicts(True, False, "invented quote")  # fails the quote check
        return grade_handler(user)

    c = FakeClient({Rubric: rubric_handler, Grading: flaky, Feedback: lambda _u: FEEDBACK})
    cfg = Settings(
        pipeline=PipelineConfig(
            rubric_selftest=False, max_workers=1, read_first=False, evidence_policy="strict"
        ),
        paths=PathsConfig(rubrics_dir=tmp_path / "c"),
    )
    out = run_items([make_item(1, "It updates weights.")], "pipeline", c, cfg, tmp_path / "r.jsonl")
    assert out[0].predicted_mark == 1.0 and "retried" in out[0].flags


def invented_quote(_user: str) -> dict:
    return verdicts(True, False, "completely invented words")


def run_with_policy(tmp_path: Path, policy: str):
    c = FakeClient({Rubric: rubric_handler, Grading: invented_quote, Feedback: lambda _u: FEEDBACK})
    cfg = Settings(
        pipeline=PipelineConfig(
            rubric_selftest=False, max_workers=1, read_first=False, evidence_policy=policy
        ),
        paths=PathsConfig(rubrics_dir=tmp_path / "c"),
    )
    out = run_items([make_item(1, "It updates weights.")], "pipeline", c, cfg, tmp_path / "r.jsonl")
    return out[0], c


def test_strict_policy_removes_credit_that_has_no_quote(tmp_path: Path):
    result, c = run_with_policy(tmp_path, "strict")
    assert result.predicted_mark == 0 and "retried" in result.flags
    assert c.count(Grading) == 2  # asked again before giving up


def test_flag_policy_keeps_credit_and_reports_it_without_retrying(tmp_path: Path):
    result, c = run_with_policy(tmp_path, "flag")
    assert result.predicted_mark == 1.0
    assert "unverified_quote:P1" in result.flags
    assert c.count(Grading) == 1  # an unfound quote alone does not cost a second call


def test_failed_selftest_is_recorded_not_fatal():
    def stingy(_user: str) -> dict:
        return verdicts(False, False, "")

    c = FakeClient({Rubric: rubric_handler, Grading: stingy})
    q = Question(key="t/q1", text="Q", model_answer=MODEL_ANSWER, max_mark=2.0)
    rec = build_record(q, c, run_selftest=True)
    assert rec.selftest_passed is False and rec.selftest_notes
    assert c.count(Rubric) == 2  # rewritten once


def partial_handler(_user: str) -> dict:
    return {"verdicts": [
        {"point_id": "P1", "status": "partial", "marks_awarded": 0.2,
         "evidence": "updates weights", "reason": "r"},
        {"point_id": "P2", "status": "not_met", "marks_awarded": 0.0, "reason": "r"},
    ]}  # fmt: skip


def test_partial_weight_decides_the_marks_not_the_model(tmp_path: Path):
    from autograde.pipeline.rescore import rescore
    from autograde.schemas import Rubric as RubricModel

    cfg = settings(tmp_path)
    cfg.pipeline.rubric_selftest = False
    cfg.pipeline.partial_weight = 0.9
    c = FakeClient({Rubric: rubric_handler, Grading: partial_handler,
                    Feedback: lambda _u: FEEDBACK, Reading: lambda _u: READING})  # fmt: skip
    out = run_items([make_item(1, "It updates weights.")], "pipeline", c, cfg, tmp_path / "a.jsonl")
    assert out[0].predicted_mark == 0.9
    assert out[0].grading.verdicts[0].model_marks == 0.2
    # re-pricing the saved verdicts needs no model and matches a real run at that weight
    rubric = RubricModel.model_validate(rubric_handler(""))
    again = rescore(out, {"t/q1": rubric}, partial_weight=0.5)
    assert again[0].predicted_mark == 0.5 and "rescored" in again[0].flags


def test_model_rule_keeps_the_models_own_marks(tmp_path: Path):
    cfg = settings(tmp_path)
    cfg.pipeline.rubric_selftest = False
    cfg.pipeline.mark_rule = "model"
    c = FakeClient({Rubric: rubric_handler, Grading: partial_handler,
                    Feedback: lambda _u: FEEDBACK, Reading: lambda _u: READING})  # fmt: skip
    out = run_items([make_item(1, "It updates weights.")], "pipeline", c, cfg, tmp_path / "b.jsonl")
    assert out[0].predicted_mark == 0.2

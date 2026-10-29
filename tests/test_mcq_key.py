"""A multiple-choice question with no answer key: the model chooses it once and says so."""

from autograde.pipeline.objective import Choice
from autograde.schemas import Feedback, Grading, Reading, RubricDraft
from fakes import FakeClient
from test_kinds_pipeline import MCQ, item, mark


def client(option="B"):
    return FakeClient(
        {
            Choice: lambda _u: {"option": option, "reason": "r"},
            Feedback: lambda _u: {"strengths": [], "improvements": [], "summary": "Overall, ok."},
            Grading: lambda _u: {"verdicts": []},
            Reading: lambda _u: {"gist": "g", "ideas": [], "problems": []},
            RubricDraft: lambda _u: {"points": []},
        }
    )


def test_with_no_key_the_model_picks_it_once_and_the_answer_is_flagged(tmp_path):
    c = client("B")
    res = mark(tmp_path, item("B", kind="mcq", marks=1.0, question=MCQ, model=""), c)
    assert res.predicted_mark == 1.0
    assert c.count(Choice) == 1 and c.count(Grading) == 0
    assert "mcq_key_derived" in res.flags


def test_a_student_who_disagrees_with_the_derived_key_loses_the_mark(tmp_path):
    res = mark(tmp_path, item("C", kind="mcq", marks=1.0, question=MCQ, model=""), client("B"))
    assert res.predicted_mark == 0 and "mcq_key_derived" in res.flags


def test_a_given_key_is_never_replaced_by_the_models_opinion(tmp_path):
    c = client("D")
    res = mark(tmp_path, item("B", kind="mcq", marks=1.0, question=MCQ, model="B"), c)
    assert res.predicted_mark == 1.0 and c.count(Choice) == 0
    assert "mcq_key_derived" not in res.flags

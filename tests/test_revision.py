from autograde.evaluation.revision import (
    Revised,
    RevisionRow,
    feedback_text,
    leakage,
    summarise,
)
from autograde.pipeline.feedback import write_feedback
from autograde.schemas import (
    Feedback,
    Grading,
    Improvement,
    Item,
    PointVerdict,
    Rubric,
    RubricPoint,
)
from fakes import FakeClient


def test_leakage_counts_shared_phrases():
    model = "the static array is initialised only once when the function is called"
    assert leakage(model, model) == 1.0
    assert leakage("nothing in common here at all", model) == 0.0
    half = "the static array is initialised only once but then something else"
    assert 0 < leakage(half, model) < 1


def test_feedback_text_includes_why_and_summary():
    fb = Feedback(
        strengths=["You named the stack."],
        improvements=[
            Improvement(point_id="P1", issue="No order.", why="Because LIFO.", fix="Add it.")
        ],
        summary="Remember LIFO.",
    )
    text = feedback_text(fb)
    assert "Because LIFO." in text and "Remember LIFO." in text and "named the stack" in text


def test_summarise_lift_is_gain_minus_control():
    rows = [
        RevisionRow(
            id="a",
            max_mark=4,
            before=2,
            with_feedback=4,
            without_feedback=3,
            leak_feedback=0.2,
            leak_revised=0.4,
        ),
        RevisionRow(
            id="b",
            max_mark=2,
            before=1,
            with_feedback=1,
            without_feedback=1,
            leak_feedback=0.0,
            leak_revised=0.0,
        ),
    ]
    s = summarise(rows)
    assert s["n"] == 2
    assert s["gain_with_feedback"] == 0.25 and s["gain_without_feedback"] == 0.125
    assert s["lift"] == 0.125 and s["share_improved"] == 0.5


def _item():
    return Item(
        id="1",
        dataset="d",
        question_id="q",
        question="Q?",
        model_answer="M",
        student_answer="S",
        max_mark=2,
        human_mark=1,
    )


def test_feedback_variants_call_counts():
    rubric = Rubric(points=[RubricPoint(id="P1", description="d", marks=2)])
    grading = Grading(
        verdicts=[
            PointVerdict(point_id="P1", status="not_met", marks_awarded=0, evidence="", reason="r")
        ]
    )
    fb = {"strengths": [], "improvements": [], "summary": "s"}
    for variant, calls in [("standard", 1), ("hints", 1), ("critique", 2)]:
        client = FakeClient({Feedback: lambda _u: fb})
        write_feedback(_item(), rubric, grading, client, variant)
        assert client.count(Feedback) == calls


def test_revised_schema():
    assert Revised(answer="x").answer == "x"


def test_leakage_works_for_indic_scripts():
    model = "प्रकाश वस्तूवरून परावर्तित होऊन डोळ्यांपर्यंत पोहोचतो तेव्हा वस्तू दिसते।"
    copied = "लक्षात ठेवा: प्रकाश वस्तूवरून परावर्तित होऊन डोळ्यांपर्यंत पोहोचतो."
    assert leakage(copied, model) > 0.3
    assert leakage("तुम्ही परावर्तनाबद्दल लिहिले नाही", model) == 0.0
    ta = "ஒளி பொருளில் பட்டு கண்ணை அடைகிறது"
    assert leakage(ta, ta) == 1.0


def test_uptake_counts_named_points_that_improved_and_harm_the_others():
    from autograde.evaluation.revision import RevisionRow, summarise

    row = RevisionRow(
        id="a",
        max_mark=4,
        before=1,
        with_feedback=3,
        without_feedback=1,
        leak_feedback=0,
        leak_revised=0,
        flagged=["P2", "P3"],
        before_marks={"P1": 1, "P2": 0, "P3": 0, "P4": 1},
        revised_verdicts=[
            {"point_id": "P1", "status": "met", "marks": 1},
            {"point_id": "P2", "status": "met", "marks": 1},
            {"point_id": "P3", "status": "not_met", "marks": 0},
            {"point_id": "P4", "status": "not_met", "marks": 0},
        ],
    )
    out = summarise([row])
    assert out["uptake"] == 0.5 and out["harm"] == 0.5

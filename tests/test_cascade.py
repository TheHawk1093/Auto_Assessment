from autograde.pipeline.cascade import unsure_because
from autograde.schemas import Deducted, Grading, PointVerdict


def verdict(status: str, marks: float) -> PointVerdict:
    return PointVerdict(point_id="P1", status=status, marks_awarded=marks, reason="x")


def test_clear_cut_marks_stay_with_the_cheap_model():
    full = Grading(verdicts=[verdict("met", 4)])
    zero = Grading(verdicts=[verdict("not_met", 0)])
    for g in (full, zero):
        assert unsure_because(g, [], 4, ["partial", "mid", "deduction"]) == []


def test_partial_and_mid_triggers():
    g = Grading(verdicts=[verdict("partial", 2)])
    assert unsure_because(g, [], 4, ["partial", "mid"]) == ["partial", "mid"]
    assert unsure_because(g, [], 4, ["mid"]) == ["mid"]


def test_deduction_and_unverified_triggers():
    d = Deducted(rule_id="D1", evidence="e", reason="r", marks=1)
    g = Grading(verdicts=[verdict("met", 4)], deductions=[d])
    assert unsure_because(g, ["unverified_quote:P1"], 4, ["deduction", "unverified"]) == [
        "unverified",
        "deduction",
    ] or set(unsure_because(g, ["unverified_quote:P1"], 4, ["deduction", "unverified"])) == {
        "unverified",
        "deduction",
    }

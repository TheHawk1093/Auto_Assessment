from autograde.pipeline.verify import apply_mark_rule, finalise_deductions
from autograde.schemas import Deducted, DeductionRule, Grading, PointVerdict, Rubric, RubricPoint


def _setup():
    rubric = Rubric(
        points=[
            RubricPoint(id="P1", description="a", marks=3),
            RubricPoint(id="P2", description="b", marks=2),
        ],
        deductions=[DeductionRule(id="D1", description="wrong statement", marks=1)],
    )
    verdicts = [
        PointVerdict(point_id="P1", status="met", marks_awarded=3, evidence="x", reason="r"),
        PointVerdict(point_id="P2", status="partial", marks_awarded=1, evidence="y", reason="r"),
    ]
    return rubric, verdicts


def test_deduction_is_taken_from_the_rule_and_needs_a_quote():
    rubric, verdicts = _setup()
    answer = "the sky is green and water is wet"
    said = Deducted(rule_id="D1", evidence="the sky is green", reason="wrong", marks=99)
    graded, flags = finalise_deductions(
        Grading(verdicts=verdicts, deductions=[said]), rubric, answer
    )
    assert graded.total == 3.0 and flags == ["deduction:D1"]  # 4 earned, 1 deducted, not 99

    invented = Deducted(rule_id="D1", evidence="not in the answer", reason="wrong")
    dropped, flags = finalise_deductions(
        Grading(verdicts=verdicts, deductions=[invented]), rubric, answer
    )
    assert dropped.total == 4.0 and flags == ["deduction_dropped:D1"]

    unknown = Deducted(rule_id="D9", evidence="the sky is green", reason="wrong")
    assert (
        finalise_deductions(Grading(verdicts=verdicts, deductions=[unknown]), rubric, answer)[
            0
        ].total
        == 4.0
    )


def test_deduction_survives_pricing_and_never_goes_below_zero():
    rubric, verdicts = _setup()
    said = Deducted(rule_id="D1", evidence="x", reason="r", marks=1)
    priced = apply_mark_rule(Grading(verdicts=verdicts, deductions=[said]), rubric, 0.5)
    assert priced.total == 3.0  # 3 + 0.5 * 2 - 1 = 3
    big = Deducted(rule_id="D1", evidence="x", reason="r", marks=50)
    assert Grading(verdicts=verdicts, deductions=[big]).total == 0.0

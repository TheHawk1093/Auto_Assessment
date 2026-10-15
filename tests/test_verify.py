from autograde.pipeline.verify import check_grading, evidence_in_answer, repair
from autograde.schemas import Grading, PointVerdict, Rubric, RubricPoint

ANSWER = 'A neural network is "massively parallel" and stores knowledge in synaptic weights.'
RUBRIC = Rubric(
    points=[
        RubricPoint(id="P1", description="parallel", marks=1),
        RubricPoint(id="P2", description="weights", marks=1),
    ]
)


def verdict(pid, status, marks, evidence="", reason="r"):
    return PointVerdict(point_id=pid, status=status, marks_awarded=marks, evidence=evidence,
                        reason=reason)  # fmt: skip


def test_evidence_ignores_case_quotes_and_spacing():
    assert evidence_in_answer("Massively   PARALLEL", ANSWER)
    assert evidence_in_answer("neural network ... synaptic weights", ANSWER)


def test_evidence_rejects_invented_or_empty_quotes():
    assert not evidence_in_answer("uses backpropagation", ANSWER)
    assert not evidence_in_answer("", ANSWER)
    assert not evidence_in_answer("neural network ... backpropagation", ANSWER)


def test_valid_grading_has_no_problems():
    g = Grading(verdicts=[verdict("P1", "met", 1, "massively parallel"),
                          verdict("P2", "not_met", 0)])  # fmt: skip
    assert check_grading(g, RUBRIC, ANSWER) == []
    assert g.total == 1


def test_problems_are_reported():
    g = Grading(
        verdicts=[
            verdict("P1", "met", 2, "massively parallel"),  # over-award
            verdict("P1", "not_met", 0),  # duplicate
            verdict("P9", "not_met", 0),  # unknown
        ]
    )
    text = " ".join(check_grading(g, RUBRIC, ANSWER))
    assert "worth 1" in text and "more than once" in text
    assert "P9" in text and "P2: no verdict" in text


def test_partial_needs_marks_strictly_between():
    g = Grading(verdicts=[verdict("P1", "partial", 1, "massively parallel"),
                          verdict("P2", "not_met", 0)])  # fmt: skip
    assert any("partial" in p for p in check_grading(g, RUBRIC, ANSWER))


def test_repair_removes_unsupported_credit_and_fills_gaps():
    g = Grading(verdicts=[verdict("P1", "met", 1, "uses backpropagation")])
    fixed, flags = repair(g, RUBRIC, ANSWER)
    assert fixed.total == 0
    assert [v.point_id for v in fixed.verdicts] == ["P1", "P2"]
    assert any("unsupported_evidence" in f for f in flags)
    assert any("missing" in f for f in flags)
    assert check_grading(fixed, RUBRIC, ANSWER) == []


def test_repair_caps_over_award():
    g = Grading(verdicts=[verdict("P1", "met", 3, "massively parallel"),
                          verdict("P2", "not_met", 0)])  # fmt: skip
    fixed, _ = repair(g, RUBRIC, ANSWER)
    assert fixed.verdicts[0].marks_awarded == 1

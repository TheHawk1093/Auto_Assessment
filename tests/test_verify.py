from autograde.pipeline.verify import (
    apply_mark_rule,
    check_grading,
    evidence_in_answer,
    repair,
    unverified_points,
)
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


def test_evidence_matches_formulas_despite_spacing_and_symbols():
    answer = "apply delta rule: W(t+1) = W(t) + n*e*X end"
    assert evidence_in_answer("W(t+1)=W(t)+n*e*X", answer)
    assert evidence_in_answer("w ( t+1 ) = w(t) + n * e * x", answer)
    assert not evidence_in_answer("gradient descent minimises the loss function", answer)


def test_squashed_match_needs_enough_characters():
    assert not evidence_in_answer("a+b", "x = a + b")


def test_unverified_points_lists_credit_without_a_found_quote():
    g = Grading(
        verdicts=[
            verdict("P1", "met", 1, "massively parallel"),
            verdict("P2", "met", 1, "made up words"),
        ]
    )
    assert unverified_points(g, ANSWER) == ["P2"]


def test_check_can_ignore_missing_quotes():
    g = Grading(verdicts=[verdict("P1", "met", 1, "made up"), verdict("P2", "not_met", 0)])
    assert check_grading(g, RUBRIC, ANSWER, require_evidence=False) == []
    assert check_grading(g, RUBRIC, ANSWER, require_evidence=True) != []


def test_repair_can_keep_unsupported_credit():
    g = Grading(verdicts=[verdict("P1", "met", 1, "made up"), verdict("P2", "not_met", 0)])
    fixed, flags = repair(g, RUBRIC, ANSWER, zero_unsupported=False)
    assert fixed.total == 1 and flags == []


def test_mark_rule_prices_verdicts_in_code():
    g = Grading(
        verdicts=[
            verdict("P1", "partial", 0.3, "massively parallel"),
            verdict("P2", "met", 1, "synaptic weights"),
        ]
    )
    priced = apply_mark_rule(g, RUBRIC, partial_weight=0.8)
    assert [v.marks_awarded for v in priced.verdicts] == [0.8, 1.0]
    assert priced.verdicts[0].model_marks == 0.3  # what the model first said is kept
    again = apply_mark_rule(priced, RUBRIC, partial_weight=0.5)
    assert again.verdicts[0].model_marks == 0.3 and again.total == 1.5  # not overwritten


def test_not_met_is_always_zero():
    g = Grading(verdicts=[verdict("P1", "not_met", 0), verdict("P2", "not_met", 0)])
    assert apply_mark_rule(g, RUBRIC, partial_weight=1.0).total == 0


def test_credit_with_no_quote_is_a_problem_even_when_unfound_quotes_are_tolerated():
    from autograde.schemas import PointVerdict

    quiet = Grading(
        verdicts=[PointVerdict(point_id="P1", status="met", marks_awarded=1, reason="r")]
        + [PointVerdict(point_id="P2", status="not_met", marks_awarded=0, reason="r")]
    )
    problems = check_grading(quiet, RUBRIC, "some answer", require_evidence=False)
    assert any("no words quoted" in p for p in problems)
    off = quiet.model_copy(
        update={
            "verdicts": [
                quiet.verdicts[0].model_copy(update={"evidence": "words not in the answer"}),
                quiet.verdicts[1],
            ]
        }
    )
    assert check_grading(off, RUBRIC, "some answer", require_evidence=False) == []

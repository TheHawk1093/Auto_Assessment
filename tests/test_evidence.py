from autograde.pipeline.verify import evidence_in_answer, repair
from autograde.schemas import Grading, PointVerdict, Rubric, RubricPoint

LONG = (
    "Backpropagation computes the error at the output layer and then passes the local "
    "gradients back through the hidden layers so that each weight can be updated."
)


def test_a_quote_with_a_corrected_typo_counts_as_a_copy():
    answer = (
        "Propagation of the output activation back through the network usin the training pattern"
    )
    quote = (
        "Propagation of the output activation back through the network using the training pattern"
    )
    assert evidence_in_answer(quote, answer)


def test_a_reworded_or_scattered_quote_does_not_count():
    reworded = "The error is computed at the output and gradients flow back to earlier layers"
    assert not evidence_in_answer(reworded, LONG)
    assert not evidence_in_answer("a b c d e f g h i j k l m n o p q r s t u v w x y z", LONG)


def test_short_quotes_must_match_exactly():
    assert not evidence_in_answer("local gradient", "The local gradiant is used")


def _one_point(answer: str, evidence: str):
    rubric = Rubric(points=[RubricPoint(id="P1", description="d", marks=2)])
    grading = Grading(
        verdicts=[
            PointVerdict(
                point_id="P1", status="met", marks_awarded=2, evidence=evidence, reason="r"
            )
        ]
    )
    return repair(grading, rubric, answer, zero_unsupported=False)


def test_unquoted_credit_on_a_one_line_answer_cites_the_answer():
    grading, flags = _one_point("a return type and input parameters", "")
    assert grading.verdicts[0].evidence == "a return type and input parameters"
    assert grading.verdicts[0].marks_awarded == 2 and not flags


def test_unquoted_credit_on_a_long_answer_is_kept_and_stays_unverified():
    from autograde.pipeline.verify import unverified_points

    long_answer = " ".join(["word"] * 40)
    grading, _ = _one_point(long_answer, "")
    assert grading.verdicts[0].marks_awarded == 2
    assert unverified_points(grading, long_answer) == ["P1"]

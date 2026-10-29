from autograde.pipeline.review import review_reasons, review_stats
from autograde.schemas import Grading, Item, PointVerdict, Result


def result(
    mark: float,
    flags: list[str] | None = None,
    statuses: tuple[str, ...] = ("met",),
    answer: str = "an answer",
    human: float | None = None,
    max_mark: float = 10,
) -> Result:
    marks = {"met": 5.0, "partial": 3.0, "not_met": 0.0}
    verdicts = [
        PointVerdict(point_id=f"P{i}", status=s, marks_awarded=marks[s], evidence="x", reason="r")
        for i, s in enumerate(statuses, 1)
    ]
    item = Item(
        id="a",
        dataset="d",
        question_id="q",
        question="q",
        model_answer="m",
        student_answer=answer,
        max_mark=max_mark,
        human_mark=human,
    )
    return Result(
        item=item,
        mode="pipeline",
        predicted_mark=mark,
        grading=Grading(verdicts=verdicts),
        flags=flags or [],
    )


def test_a_clean_result_is_not_listed():
    assert review_reasons(result(10, statuses=("met", "met"))) == []


def test_each_trouble_sign_gives_its_reason():
    assert review_reasons(result(10, ["retried"])) == ["marking_unstable"]
    assert review_reasons(result(10, ["scheme_failed_selftest"])) == ["scheme_unreliable"]
    assert review_reasons(result(10, ["unverified_quote:P1"])) == ["credit_unquoted"]
    assert review_reasons(result(10, ["models_disagree"])) == ["models_disagree"]
    assert review_reasons(result(10, ["keyword_list_capped"])) == ["form_or_deduction"]
    assert review_reasons(result(10, ["figure_not_checked"])) == ["figure_unchecked"]
    assert review_reasons(result(10, answer="the [?valve?] opens")) == ["ocr_unsure"]


def test_empty_and_nonsense_answers_are_never_listed():
    assert review_reasons(result(0, ["empty_answer", "retried"])) == []
    assert review_reasons(result(0, ["incoherent_answer", "unverified_quote:P1"])) == []


def test_a_close_call_needs_mid_range_and_real_partial_credit():
    assert review_reasons(result(8, statuses=("met", "partial"), max_mark=20)) == []  # 3 of 20 only
    mid = result(6, statuses=("partial", "partial"), max_mark=10)  # partial marks 6 >= 2
    assert review_reasons(mid) == ["ambiguous_partial"]
    assert review_reasons(result(9, statuses=("partial", "partial"))) == []  # not mid-range


def test_stats_compare_listed_answers_with_the_rest():
    bad = result(2, ["retried"], human=9)
    good = result(9, human=9)
    stats = review_stats([bad, good])
    assert stats["listed"] == 1 and stats["share_of_bad_caught"] == 1.0
    assert stats["error_listed"] > stats["error_not_listed"]

import pytest

from autograde.pipeline.numeric import check_number, decide_numeric, find_numbers, parse_unit
from autograde.schemas import Grading, NumericSpec, PointVerdict, Rubric, RubricPoint


def spec(value, unit="", rel_tol=0.01, unit_share=0.2):
    return NumericSpec(value=value, unit=unit, rel_tol=rel_tol, unit_share=unit_share)


@pytest.mark.parametrize(
    "text, factor, dims",
    [
        ("m/s", 1, (1, 0, -1, 0, 0, 0, 0)),
        ("km/h", 1000 / 3600, (1, 0, -1, 0, 0, 0, 0)),
        ("kg*m/s^2", 1, (1, 1, -2, 0, 0, 0, 0)),
        ("m/s²", 1, (1, 0, -2, 0, 0, 0, 0)),
        ("kΩ", 1000, (2, 1, -3, -2, 0, 0, 0)),
        ("mA", 1e-3, (0, 0, 0, 1, 0, 0, 0)),
        ("N", 1, (1, 1, -2, 0, 0, 0, 0)),
        ("kN", 1000, (1, 1, -2, 0, 0, 0, 0)),
        ("cm", 0.01, (1, 0, 0, 0, 0, 0, 0)),
    ],
)
def test_units_have_the_right_size_and_dimension(text, factor, dims):
    got = parse_unit(text)
    assert got is not None and got[1] == dims and got[0] == pytest.approx(factor)


def test_unknown_units_are_not_guessed():
    assert parse_unit("widgets") is None


@pytest.mark.parametrize(
    "answer, value, unit",
    [
        ("The speed is 12 m/s.", 12, "m/s"),
        ("v = 1.2e1 m/s", 12, "m/s"),
        ("12.0 × 10^0 m/s", 12, "m/s"),
        ("1,200 mm", 1200, "mm"),
    ],
)
def test_numbers_are_found_with_their_units(answer, value, unit):
    found = find_numbers(answer)
    assert found and found[-1].value == pytest.approx(value) and found[-1].unit == unit


def test_right_number_and_unit_in_a_different_unit_is_correct():
    res = check_number("so L = 150 cm", spec(1.5, "m"))
    assert res.value_ok and res.unit == "ok"


def test_wrong_scale_is_a_wrong_value_not_a_wrong_unit():
    res = check_number("L = 1.5 km", spec(1.5, "m"))
    assert not res.value_ok


def test_missing_unit_is_reported_separately_from_a_wrong_value():
    res = check_number("The answer is 9.81", spec(9.81, "m/s^2"))
    assert res.value_ok and res.unit == "missing"


def test_right_number_with_the_wrong_kind_of_unit():
    res = check_number("F = 9.81 kg", spec(9.81, "N"))
    assert res.value_ok and res.unit == "wrong"


def test_tolerance_is_respected():
    assert check_number("g = 9.85 m/s^2", spec(9.81, "m/s^2", rel_tol=0.01)).value_ok
    assert not check_number("g = 10.5 m/s^2", spec(9.81, "m/s^2", rel_tol=0.01)).value_ok


def test_the_last_matching_number_wins_over_working():
    res = check_number("2 x 3 = 6 N, then 6 + 4 = 10 N", spec(10, "N"))
    assert res.value_ok and res.unit == "ok"


def test_no_number_at_all():
    res = check_number("I think it is large", spec(10, "N"))
    assert not res.found and not res.value_ok


def _grading(status="met", marks=2.0):
    return Grading(
        verdicts=[PointVerdict(point_id="P1", status=status, marks_awarded=marks, reason="x")]
    )


def _rubric(unit_share=0.25):
    return Rubric(
        points=[
            RubricPoint(
                id="P1",
                description="final answer",
                marks=2,
                numeric=spec(10, "N", unit_share=unit_share),
            )
        ]
    )


def test_code_overrides_a_model_that_credited_a_wrong_number():
    graded, note, flags = decide_numeric(_grading("met", 2.0), _rubric(), "F = 12 N")
    assert graded.total == 0 and graded.verdicts[0].status == "not_met" and not flags
    assert "do not match" in note


def test_missing_unit_loses_only_the_unit_share():
    graded, _, flags = decide_numeric(_grading("not_met", 0.0), _rubric(0.25), "F = 10")
    assert graded.total == pytest.approx(1.5) and graded.verdicts[0].status == "partial"
    assert flags == ["unit_missing:P1"]


def test_correct_answer_gets_full_marks_even_if_the_model_missed_it():
    graded, _, _ = decide_numeric(_grading("not_met", 0.0), _rubric(), "so F = 0.01 kN")
    assert graded.total == 2 and graded.verdicts[0].status == "met"


def test_a_wrong_number_still_says_whether_its_unit_was_right():
    # the feedback writer must not claim a unit is missing when it is there
    res = check_number("KE = 0.5 x 1000 x 20 = 10000 J", spec(200000, "J"))
    assert not res.value_ok and res.final_unit == "ok" and "10000 J" in res.final
    from autograde.pipeline.numeric import describe_result

    said = describe_result(spec(200000, "J"), res)
    assert "its unit is right" in said and "do not match" in said
    bare = check_number("KE = 10000", spec(200000, "J"))
    assert bare.final_unit == "missing" and "it has no unit" in describe_result(
        spec(200000, "J"), bare
    )


def test_a_minus_set_apart_from_its_number_still_makes_it_negative():
    from autograde.pipeline.numeric import check_number, find_numbers
    from autograde.schemas import NumericSpec

    answer = "I used G = (1-F)/(-2) = -0.0906346. So: xk+1 = 0.818731xk - 0.0906346uk"
    assert [c.value for c in find_numbers("a - 0.5u")] == [-0.5]
    assert not check_number(answer, NumericSpec(value=0.090635)).value_ok  # the sign was flipped
    assert check_number("G = 0.0906", NumericSpec(value=0.090635)).value_ok

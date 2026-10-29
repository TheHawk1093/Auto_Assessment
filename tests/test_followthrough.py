"""Multi-part questions: later parts are marked on the student's own earlier results."""

from autograde.pipeline.run import run_items
from autograde.schemas import Grading
from test_kinds_pipeline import NUMERIC_POINTS, client, item, mark, settings


def test_a_later_part_sees_the_earlier_answers_only_when_follow_through_is_on(tmp_path):
    later = item("F = 15 N", kind="numeric", earlier="Part 2a: m = 3 kg")
    on, off = client(NUMERIC_POINTS, "met", 2.0), client(NUMERIC_POINTS, "met", 2.0)
    mark(tmp_path, later, on)
    cfg = settings(tmp_path / "off", follow_through=False)
    run_items([later], "pipeline", off, cfg, tmp_path / "off.jsonl")
    assert any("Part 2a: m = 3 kg" in u for m, u in on.calls if m is Grading)
    assert not any("Part 2a" in u for m, u in off.calls if m is Grading)


def test_follow_through_leaves_a_different_number_to_the_marker_and_flags_it(tmp_path):
    later = item("F = 15 N", kind="numeric", earlier="Part 2a: m = 3 kg")
    res = mark(tmp_path, later, client(NUMERIC_POINTS, "met", 2.0))
    assert res.predicted_mark == 2.0  # the marker's verdict stands: 15 N may be right for their m
    assert "follow_through_unchecked:P1" in res.flags


def test_without_earlier_parts_a_wrong_number_is_still_zeroed_by_code(tmp_path):
    res = mark(tmp_path, item("F = 15 N", kind="numeric"), client(NUMERIC_POINTS, "met", 2.0))
    assert res.predicted_mark == 0


def test_a_right_number_is_still_credited_by_code_in_a_later_part(tmp_path):
    later = item("F = 10 N", kind="numeric", earlier="Part 2a: m = 1 kg")
    res = mark(tmp_path, later, client(NUMERIC_POINTS, "not_met", 0.0))
    assert res.predicted_mark == 2.0


def test_a_false_claim_that_the_unit_is_missing_is_removed_from_the_marker_note(tmp_path):
    from autograde.pipeline.numeric import decide_numeric
    from autograde.schemas import Grading, PointVerdict, Rubric, RubricPoint

    rubric = Rubric(
        points=[
            RubricPoint(
                id="P1", description="final answer", marks=2, numeric=NUMERIC_POINTS[0]["numeric"]
            )
        ]
    )
    rubric = Rubric.model_validate(rubric.model_dump())
    said = "The final answer is missing the required unit of Newtons."
    graded = Grading(
        verdicts=[PointVerdict(point_id="P1", status="partial", marks_awarded=1.0, reason=said)]
    )
    out, _, flags = decide_numeric(graded, rubric, "F = 250 N", follow_through=True)
    assert "missing the required unit" not in out.verdicts[0].reason
    assert "its unit is right" in out.verdicts[0].reason
    assert out.verdicts[0].marks_awarded == 1.0  # the marker's marks stand
    assert "reason_corrected:P1" in flags and "follow_through_unchecked:P1" in flags

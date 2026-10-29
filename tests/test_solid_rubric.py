"""The solid scheme writer: part-mark levels, teacher inputs, derived answer keys, review."""

from autograde.config import TeacherInputs
from autograde.pipeline.rubric import (
    build_record,
    conform,
    full_credit_text,
    teacher_block,
    variant_dir,
)
from autograde.pipeline.verify import allowed_shares, apply_mark_rule, snap
from autograde.schemas import (
    NO_REFERENCE,
    Grading,
    Item,
    PointVerdict,
    Question,
    Rubric,
    RubricDraft,
    RubricLevel,
    RubricPoint,
    RubricReview,
)
from fakes import FakeClient

LEVELS = [RubricLevel(share=0.25, says="names it"), RubricLevel(share=0.75, says="uses it")]


def rubric(levels: list[RubricLevel] | None = None) -> Rubric:
    return Rubric(
        points=[
            RubricPoint(id="P1", description="a", marks=2, levels=levels or []),
            RubricPoint(id="P2", description="b", marks=2),
        ]
    )


def partial(pid: str, proposed: float) -> PointVerdict:
    return PointVerdict(point_id=pid, status="partial", marks_awarded=proposed, reason="r")


def test_snap_picks_the_nearest_allowed_share_and_the_lower_on_a_tie():
    assert snap(0.6, (0.25, 0.75)) == 0.75
    assert snap(0.5, (0.25, 0.75)) == 0.25
    assert snap(0.5, ()) == 0.0


def test_a_partial_verdict_takes_the_point_levels_when_there_are_some():
    g = Grading(verdicts=[partial("P1", 1.4), partial("P2", 1.0)])  # 70% and 50% of 2
    out = apply_mark_rule(g, rubric(LEVELS), partial_weight=0.5)
    assert [v.marks_awarded for v in out.verdicts] == [1.5, 1.0]  # P1 snapped to 0.75, P2 default


def test_teacher_granularity_sets_the_shares_of_points_without_levels():
    g = Grading(verdicts=[partial("P2", 0.9)])
    assert allowed_shares(None, 0.5, "quarter") == (0.25, 0.5, 0.75)
    assert apply_mark_rule(g, rubric(), 0.5, "quarter").verdicts[0].marks_awarded == 1.0
    assert apply_mark_rule(g, rubric(), 0.5, "none").verdicts[0].marks_awarded == 0.0


def test_repricing_starts_from_the_models_own_figure():
    g = Grading(verdicts=[partial("P1", 1.4)])
    once = apply_mark_rule(g, rubric(LEVELS), 0.5)
    again = apply_mark_rule(once, rubric(LEVELS), 0.5)
    assert once.verdicts[0].marks_awarded == again.verdicts[0].marks_awarded == 1.5


def test_conform_follows_the_teachers_granularity():
    mixed = rubric([RubricLevel(share=0.3, says="x"), RubricLevel(share=0.7, says="y")])
    assert [lv.share for lv in conform(mixed, "half").points[0].levels] == [0.5]
    assert conform(mixed, "none").points[0].levels == []
    assert conform(mixed, "rubric") == mixed


def test_the_cache_folder_changes_only_when_the_teacher_input_changes_the_scheme():
    assert variant_dir("solid", TeacherInputs()) == "solid"
    assert variant_dir("generated", TeacherInputs(partial_credit="half")) == "generated"
    a = variant_dir("solid", TeacherInputs(partial_credit="half"))
    assert a.startswith("solid-") and a != variant_dir("solid", TeacherInputs(notes="units"))


def test_teacher_block_lists_only_what_was_said():
    assert teacher_block(TeacherInputs(), "d/q") == ""
    t = TeacherInputs(
        partial_credit="none", notes="Units needed.", question_notes={"d/q": "Be firm."}
    )
    text = teacher_block(t, "d/q")
    assert "not allowed" in text and "Units needed. Be firm." in text
    assert "Be firm" not in teacher_block(t, "d/other")


def test_a_missing_model_answer_is_replaced_by_the_derived_key():
    item = Item(
        id="x/1", dataset="x", question_id="1", question="Q", model_answer=NO_REFERENCE,
        student_answer="a", max_mark=1,
    )  # fmt: skip
    assert item.with_key("The key.").model_answer == "The key."
    real = item.model_copy(update={"model_answer": "Real."})
    assert real.with_key("The key.").model_answer == "Real."


def test_full_credit_text_by_kind():
    r = rubric().model_copy(update={"answer_key": "KEY"})
    q = Question(key="t/1", text="Q", model_answer="MODEL", max_mark=4)
    assert full_credit_text(q, r) == "MODEL"
    assert full_credit_text(q.model_copy(update={"model_answer": NO_REFERENCE}), r) == "KEY"
    assert full_credit_text(q.model_copy(update={"kind": "maths"}), r) == "KEY"
    assert full_credit_text(q.model_copy(update={"kind": "essay"}), r) == ""


def draft(_user: str) -> dict:
    return {
        "points": [{"id": "P1", "description": "d", "marks": 2.0}],
        "answer_key": "The answer.",
    }


def test_review_runs_without_a_model_answer_and_its_fix_is_used():
    fixed = {"points": [{"id": "P1", "description": "better", "marks": 2.0}], "notes": "n"}
    review = {"issues": ["P1 was vague."], "revised": fixed}
    full = {"verdicts": [{"point_id": "P1", "status": "met", "marks_awarded": 2.0,
                          "evidence": "The answer.", "reason": "r"}]}  # fmt: skip
    c = FakeClient({RubricDraft: draft, RubricReview: lambda _u: review, Grading: lambda _u: full})
    q = Question(key="t/1", text="Q", model_answer=NO_REFERENCE, max_mark=2.0)
    rec = build_record(q, c, run_selftest=False, variant="solid", review="no_reference")
    assert rec.rubric.points[0].description == "better"
    assert rec.rubric.answer_key == "The answer."  # kept from the draft
    assert rec.review_notes == ["P1 was vague."]


def test_no_review_when_a_model_answer_exists():
    c = FakeClient({RubricDraft: draft})
    q = Question(key="t/1", text="Q", model_answer="Real answer.", max_mark=2.0)
    build_record(q, c, run_selftest=False, variant="solid", review="no_reference")
    assert c.count(RubricReview) == 0


def test_a_missing_config_file_is_an_error_not_the_defaults(tmp_path):
    import pytest

    from autograde.config import load_settings

    with pytest.raises(FileNotFoundError):
        load_settings(tmp_path / "nope.yaml")


def test_solid_style_adds_its_prompt_and_keeps_the_solid_behaviour():
    from autograde.pipeline.rubric import is_solid, rubric_prompt

    assert is_solid("solid") and is_solid("solid.core") and not is_solid("solidly")
    assert "Style: core first" in rubric_prompt("solid.core")
    assert "Style: core first" not in rubric_prompt("solid")

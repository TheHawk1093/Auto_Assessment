"""Exam-wide rules read from the paper and rubric, and the 'stated' part-mark mode."""

from __future__ import annotations

from autograde.config import TeacherInputs
from autograde.intake.models import ExamRules
from autograde.intake.rules import apply_rules, extract_rules
from autograde.pipeline.rubric import PART_MARKS, teacher_block
from autograde.pipeline.verify import allowed_shares
from autograde.schemas import RubricLevel, RubricPoint
from fakes import FakeClient


def _apply(rules: ExamRules, **kw) -> TeacherInputs:
    args = dict(
        granularity=None,
        mark_step=None,
        strictness=None,
        follow_through=None,
        working_required=False,
        notes="",
        question_notes={},
    )
    return apply_rules(rules, **{**args, **kw})


def test_rules_become_teacher_inputs_and_teacher_flags_win():
    rules = ExamRules(
        working_required=True,
        part_marks="stated_only",
        follow_through=True,
        notes=["Deduct 0.5 for a missing unit."],
    )
    t = _apply(rules, notes="Be brief.")
    assert t.partial_credit == "stated" and t.working_required and t.follow_through
    assert t.notes == "Be brief. Deduct 0.5 for a missing unit."
    t = _apply(rules, granularity="half", follow_through=False)
    assert t.partial_credit == "half" and t.follow_through is False


def test_no_rules_leave_the_defaults_alone():
    assert _apply(ExamRules()) == TeacherInputs()
    assert not ExamRules().found


def test_extract_rules_reads_the_documents(tmp_path):
    paper = tmp_path / "paper.txt"
    paper.write_text("Instruction 5: a final answer without the formula earns no credit.")
    rubric = tmp_path / "rubric.txt"
    rubric.write_text("Every split is a whole mark.")
    client = FakeClient({ExamRules: lambda user: {"working_required": True}})
    rules = extract_rules(paper, [rubric], client)
    assert rules.working_required
    assert "without the formula" in client.calls[0][1] and "whole mark" in client.calls[0][1]


def test_stated_mode_gives_partial_credit_only_where_the_rubric_has_levels():
    plain = RubricPoint(id="P1", description="d", marks=1.0)
    levelled = RubricPoint(
        id="P2", description="d", marks=2.0, levels=[RubricLevel(share=0.5, says="half")]
    )
    assert allowed_shares(plain, 0.5, "stated") == ()  # all or nothing
    assert allowed_shares(levelled, 0.5, "stated") == (0.5,)
    assert allowed_shares(plain, 0.5, "rubric") == (0.5,)  # the old default share is unchanged


def test_stated_mode_tells_the_scheme_writer_not_to_add_levels():
    block = teacher_block(TeacherInputs(partial_credit="stated"), "k")
    assert PART_MARKS["stated"] in block and "do not add levels" in block

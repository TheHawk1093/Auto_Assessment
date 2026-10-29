"""Exam intake: question paper, reference files, answers, and how they become items."""

import json
import zipfile

import pytest

from autograde.intake.answers import _Split, load_answers, norm, split_text
from autograde.intake.exam import build_items, exam_key, marks_csv
from autograde.intake.files import read_document
from autograde.intake.models import Paper, QuestionSpec, Reference
from autograde.intake.paper import _Draft, load_paper
from autograde.intake.reference import _Draft as _RefDraft
from autograde.intake.reference import load_references
from autograde.ocr.sheets import Sheet, SheetItem
from autograde.pipeline.rubric import structured_rubric
from autograde.schemas import NOT_GIVEN, Item, Question, Result
from fakes import FakeClient

PAPER = Paper(
    questions=[
        QuestionSpec(id="1", text="Explain TCP.", max_mark=4),
        QuestionSpec(id="2a", text="Define BDP.", max_mark=2),
        QuestionSpec(id="2b", text="Compute BDP.", max_mark=3),
    ]
)


def test_markers_are_found_in_common_layouts():
    text = "Q1. first\nmore\n\nAnswer 2(a): second\n\n2 b) third"
    assert split_text(text, PAPER) == {"1": "first\nmore", "2a": "second", "2b": "third"}


def test_the_model_splits_text_without_markers():
    c = FakeClient({_Split: lambda _u: {"answers": {"1": "a", "2a": "b"}}})
    assert split_text("one long unlabelled answer", PAPER, c) == {"1": "a", "2a": "b"}
    assert c.count(_Split) == 1


def test_question_ids_compare_loosely():
    assert norm("Q2(a)") == norm("2.a") == norm("2A") == "2a"


def test_ocr_sheets_are_matched_to_the_paper(tmp_path):
    sheet = Sheet(
        sheet="s1",
        student="Dana",
        items=[
            SheetItem(question_id="1", student_answer="ans one"),
            SheetItem(question_id="2(a)", student_answer="ans two"),
            SheetItem(question_id="9", student_answer="stray"),
        ],
    )
    (tmp_path / "s1.sheet.json").write_text(sheet.model_dump_json(), encoding="utf-8")
    answers, warnings = load_answers(tmp_path, PAPER)
    assert answers == {"Dana": {"1": "ans one", "2a": "ans two"}}
    assert any("unknown question '9'" in w for w in warnings)
    assert any("no answer found for 2b" in w for w in warnings)


def test_a_json_paper_needs_no_model(tmp_path):
    f = tmp_path / "p.json"
    f.write_text(json.dumps(PAPER.model_dump()), encoding="utf-8")
    assert load_paper(f).ids == ["1", "2a", "2b"]


def test_the_model_reads_a_free_text_paper_and_missing_marks_are_refused(tmp_path):
    f = tmp_path / "p.md"
    f.write_text("Q1 Explain TCP. [4]", encoding="utf-8")
    ok = FakeClient(
        {_Draft: lambda _u: {"questions": [{"id": "1", "text": "Explain TCP.", "max_mark": 4}]}}
    )
    assert load_paper(f, ok).total == 4
    bad = FakeClient({_Draft: lambda _u: {"questions": [{"id": "1", "text": "Explain TCP."}]}})
    with pytest.raises(ValueError, match="No marks found"):
        load_paper(f, bad)


def test_duplicate_question_ids_are_refused():
    with pytest.raises(ValueError, match="more than once"):
        Paper(questions=[QuestionSpec(id="1", text="a", max_mark=1)] * 2)


def test_json_references_may_hold_either_part_and_are_merged(tmp_path):
    a = tmp_path / "answers.json"
    a.write_text(json.dumps({"1": "Model one", "2a": {"model_answer": "M2a"}}), encoding="utf-8")
    b = tmp_path / "rubrics.json"
    b.write_text(json.dumps({"1": {"rubric": "1 mark each"}}), encoding="utf-8")
    refs, warnings = load_references([a, b], PAPER)
    assert refs["1"] == Reference(model_answer="Model one", rubric="1 mark each")
    assert refs["2a"].model_answer == "M2a"
    assert any("No reference for question 2b" in w for w in warnings)


def test_text_references_go_through_the_model(tmp_path):
    f = tmp_path / "ref.md"
    f.write_text("Guide...", encoding="utf-8")
    entries = {
        "entries": [
            {"id": "1", "model_answer": "MA", "rubric": "R"},
            {"id": "zz", "model_answer": "x"},
        ]
    }
    c = FakeClient({_RefDraft: lambda _u: entries})
    refs, warnings = load_references([f], PAPER, c)
    assert list(refs) == ["1"] and any("unknown question: zz" in w for w in warnings)


def test_items_share_a_dataset_key_that_changes_with_the_references():
    refs = {"1": Reference(model_answer="M")}
    key = exam_key("quiz", PAPER, refs)
    assert key != exam_key("quiz", PAPER, {"1": Reference(model_answer="M changed")})
    items = build_items(key, PAPER, refs, {"Ann Lee": {"1": "x"}, "Bo": {}})
    assert len(items) == 6 and items[0].id == f"{key}/Ann-Lee/1"
    assert {i.question_key for i in items if i.question_id == "1"} == {f"{key}/1"}
    assert items[0].model_answer == "M" and items[1].model_answer == ""
    assert [i.student_answer for i in items if i.question_id == "1"] == ["x", ""]


def test_a_rubric_without_a_model_answer_counts_as_a_reference():
    item = Item(id="a", dataset="d", question_id="1", question="Q", model_answer="",
                rubric="1 mark for X", student_answer="s", max_mark=1)  # fmt: skip
    assert item.has_ref
    bare = item.model_copy(update={"rubric": ""})
    assert not bare.has_ref and bare.with_key("KEY").model_answer == "KEY"
    assert item.with_key("KEY").model_answer == ""


def test_a_teacher_rubric_that_is_already_points_is_used_as_given():
    rubric = {"points": [{"id": "P1", "description": "x", "marks": 2}]}
    q = Question(key="d/1", text="Q", model_answer=NOT_GIVEN, max_mark=2, rubric=json.dumps(rubric))
    assert structured_rubric(q).total == 2
    assert structured_rubric(q.model_copy(update={"max_mark": 3})) is None  # marks do not add up
    assert structured_rubric(q.model_copy(update={"rubric": "plain words"})) is None


def test_docx_text_is_read_without_extra_libraries(tmp_path):
    f = tmp_path / "p.docx"
    run = "<w:r><w:t>Q1 Explain &amp; discuss</w:t></w:r>"
    xml = f"<w:document><w:body><w:p>{run}</w:p></w:body></w:document>"
    with zipfile.ZipFile(f, "w") as zf:
        zf.writestr("word/document.xml", xml)
    assert read_document(f) == "Q1 Explain & discuss"


def test_marks_table_has_one_row_per_student():
    items = build_items("k", PAPER, {}, {"Ann": {}})
    results = [
        Result(item=i, mode="pipeline", predicted_mark=1.5 if i.question_id == "1" else 0.5)
        for i in items
    ]
    assert marks_csv(PAPER, results).splitlines() == [
        "student,1,2a,2b,total",
        "Ann,1.5,0.5,0.5,2.5",
    ]


def test_later_parts_carry_the_earlier_answers_of_the_same_question():
    from autograde.intake.exam import build_items
    from autograde.intake.models import Paper, QuestionSpec

    paper = Paper(
        questions=[
            QuestionSpec(id="1", text="Q1", max_mark=1),
            QuestionSpec(id="2a", text="Q2a", max_mark=2),
            QuestionSpec(id="2b", text="Q2b", max_mark=2),
            QuestionSpec(id="2c", text="Q2c", max_mark=2),
            QuestionSpec(id="3", text="Q3", max_mark=1),
        ]
    )
    answers = {"amy": {"1": "one", "2a": "m = 3 kg", "2b": "F = 30 N", "2c": "x", "3": "three"}}
    items = {i.question_id: i for i in build_items("k", paper, {}, answers)}
    assert items["1"].earlier == "" and items["2a"].earlier == "" and items["3"].earlier == ""
    assert items["2b"].earlier == "Part 2a: m = 3 kg"
    assert items["2c"].earlier == "Part 2a: m = 3 kg\nPart 2b: F = 30 N"

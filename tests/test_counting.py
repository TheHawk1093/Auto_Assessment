"""Best-of-n totals and struck-out questions."""

from __future__ import annotations

from autograde.intake.counting import Counting, counted_total, group_of, parse_struck
from autograde.intake.exam import marks_csv, student_markdown
from autograde.intake.models import Paper, QuestionSpec
from autograde.schemas import Item, Result


def _paper() -> Paper:
    qs = [QuestionSpec(id=i, text="t", max_mark=m) for i, m in
          [("1a", 4), ("1b", 6), ("2", 10), ("3a", 5), ("3b", 5), ("4", 10)]]  # fmt: skip
    return Paper(questions=qs)


def test_group_of_is_the_top_level_question():
    assert [group_of(i) for i in ("1a", "2", "3bii", "A")] == ["1", "2", "3", "A"]


def test_best_three_of_four_and_struck_out_question_is_skipped():
    paper = _paper()
    marks = {"1a": 4, "1b": 6, "2": 3, "3a": 5, "3b": 4, "4": 8}
    c = counted_total(marks, paper, "s", Counting(count=3))
    assert (c.total, c.out_of, c.groups) == (27, 30, ["1", "3", "4"])
    # a struck-out question is not counted even when it scored the most
    c = counted_total(marks, paper, "s", Counting(count=3, struck={"s": {"1"}}))
    assert c.groups == ["2", "3", "4"] and c.total == 20
    # no count: everything counts
    assert counted_total(marks, paper, "s", Counting()).out_of == 40


def test_parse_struck_accepts_q_prefix_and_lists():
    assert parse_struck(["a=Q3", "a=1,2", "b=4"]) == {"a": {"3", "1", "2"}, "b": {"4"}}


def _result(student: str, qid: str, mark: float) -> Result:
    item = Item(id=f"x/{student}/{qid}", dataset="x", question_id=qid, question="q",
                model_answer="", student_answer="a", max_mark=1.0)  # fmt: skip
    return Result(item=item, mode="pipeline", predicted_mark=mark)


def test_outputs_show_counted_total_and_the_struck_question():
    paper = _paper()
    counting = Counting(count=3, struck={"s": {"2"}})
    results = [_result("s", q.id, q.max_mark / 2) for q in paper.questions if group_of(q.id) != "2"]
    csv = marks_csv(paper, results, counting)
    assert csv.splitlines()[0].endswith("counted_total,counted_out_of,counted_questions")
    assert csv.splitlines()[1].endswith(",15,30,1+3+4")
    md = student_markdown("s", paper, results, counting)
    assert "struck out by the student, not marked" in md and "Counted questions: 1, 3, 4." in md

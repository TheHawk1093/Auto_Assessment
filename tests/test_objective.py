import pytest

from autograde.pipeline.objective import choices_in, mark_mcq, mcq_rubric, parse_options
from autograde.pipeline.run import to_question
from autograde.schemas import Item

QUESTION = """Which of the following is an ensemble method based on decision trees?
A. Support Vector Machine
B. Random Forest
C. K-Nearest Neighbors
D. Logistic Regression"""


def item(answer, key="B", question=QUESTION, max_mark=1.0):
    return Item(
        id="i", dataset="d", question_id="q1", question=question, model_answer=key,
        student_answer=answer, max_mark=max_mark, kind="mcq",
    )  # fmt: skip


def test_options_are_read_from_lines_and_inline():
    assert parse_options(QUESTION)["B"] == "Random Forest"
    inline = "Pick one: (a) red (b) green (c) blue"
    assert parse_options(inline) == {"A": "red", "B": "green", "C": "blue"}
    assert parse_options("What is 2+2?") == {}


@pytest.mark.parametrize(
    "answer",
    ["B", "b", "(b)", "B.", "Option B", "the answer is B", "B. Random Forest", "random forest"],
)
def test_many_ways_of_writing_the_right_choice_are_all_read_as_b(answer):
    opts = parse_options(QUESTION)
    assert choices_in(answer, opts) == {"B"}


def test_a_leading_article_is_not_mistaken_for_option_a():
    assert choices_in("A random forest builds many trees", parse_options(QUESTION)) == set()


def test_several_choices_are_read_as_a_set():
    opts = parse_options(QUESTION)
    assert choices_in("A and C", opts) == {"A", "C"}
    assert choices_in("a, c", opts) == {"A", "C"}


def test_right_choice_earns_full_marks_without_a_model():
    q = to_question(item("(b)"))
    graded, flags = mark_mcq(item("(b)"), mcq_rubric(q))
    assert graded.total == 1.0 and not flags


def test_wrong_choice_earns_nothing_and_says_what_was_right():
    q = to_question(item("C"))
    graded, flags = mark_mcq(item("C"), mcq_rubric(q))
    assert graded.total == 0 and "correct choice is B" in graded.verdicts[0].reason and not flags


def test_unclear_and_double_answers_are_flagged_not_guessed():
    q = to_question(item(""))
    assert mark_mcq(item("not sure"), mcq_rubric(q))[1] == ["unclear_choice"]
    assert mark_mcq(item("A and B"), mcq_rubric(q))[1] == ["multiple_choices"]


def test_unreadable_key_needs_checking():
    broken = item("B", key="see notes")
    assert mark_mcq(broken, mcq_rubric(to_question(broken)))[1] == ["mcq_key_unreadable"]


def test_options_flattened_onto_one_line_are_still_found():
    flat = (
        "Which of the following is an ensemble method based on decision trees? "
        "A. Support Vector Machine B. Random Forest C. K-Nearest Neighbors D. Logistic Regression"
    )
    assert parse_options(flat) == {
        "A": "Support Vector Machine",
        "B": "Random Forest",
        "C": "K-Nearest Neighbors",
        "D": "Logistic Regression",
    }
    assert choices_in("Random Forest", parse_options(flat)) == {"B"}


def test_a_sentence_containing_a_capital_a_is_not_read_as_options():
    assert parse_options("A. Einstein wrote about it. B. Describe his method.") == {}

import random

from autograde.evaluation.robustness import (
    CODE_PERTURBATIONS,
    Rewritten,
    Shift,
    perturbed,
    rewrite,
    summarise,
)
from autograde.schemas import Item
from fakes import FakeClient

ANSWER = "A stack stores elements and removes the most recent one first. It is called LIFO."


def item(text: str = ANSWER) -> Item:
    return Item(
        id="a",
        dataset="d",
        question_id="q",
        question="What is a stack?",
        model_answer="A LIFO structure.",
        student_answer=text,
        max_mark=5,
    )


def apply(name: str, text: str = ANSWER) -> str | None:
    writer = FakeClient({Rewritten: lambda user: {"answer": "x"}})
    return perturbed(item(text), name, random.Random(1), writer, {})


def test_spelling_changes_words_but_keeps_the_length_close_and_is_repeatable():
    a, b = apply("spelling"), apply("spelling")
    assert a == b != ANSWER
    assert abs(len(a) - len(ANSWER)) <= len(ANSWER.split())


def test_case_and_punctuation_keep_the_words():
    out = apply("case_punctuation")
    assert out == out.lower() and "," not in out
    assert apply("case_punctuation", "Cost is 3.5 units.") == "cost is 3.5 units"


def test_shuffled_sentences_needs_two_sentences_and_keeps_them_all():
    assert apply("shuffled_sentences", "Only one sentence here.") is None
    out = apply("shuffled_sentences")
    assert sorted(out.split()) == sorted(ANSWER.split())


def test_the_english_only_ones_skip_other_languages():
    hindi = "स्टैक एक डेटा संरचना है जिसमें अंतिम तत्व पहले निकलता है।"
    assert apply("text_speak", hindi) is None and apply("filler", hindi) is None
    assert apply("filler") is not None


def test_half_the_answer_needs_a_long_enough_answer_and_is_shorter():
    assert apply("half_the_answer", "Too short") is None
    assert len(apply("half_the_answer").split()) < len(ANSWER.split())


def test_the_question_is_repeated_in_front():
    assert apply("question_repeated").startswith("What is a stack?")


def test_a_model_rewrite_is_made_once_per_style_and_answer():
    writer = FakeClient({Rewritten: lambda user: {"answer": "rewritten"}})
    cache: dict[str, str] = {}
    assert rewrite(item(), "paraphrase", writer, cache) == "rewritten"
    rewrite(item(), "paraphrase", writer, cache)
    rewrite(item(), "informal", writer, cache)
    assert writer.count(Rewritten) == 2


def test_summary_reports_moves_and_direction():
    shifts = [
        Shift("spelling", "a", 5, 4, 4),
        Shift("spelling", "b", 5, 4, 3),
        Shift("spelling", "c", 5, 2, 3),
    ]
    row = summarise(shifts)["spelling"]
    assert row["n"] == 3 and row["moved"] == 0.667 and row["went_down"] == 0.333
    assert row["mean_shift"] == 0.0


def test_every_code_perturbation_has_a_name_in_the_public_list():
    from autograde.evaluation.robustness import NAMES

    assert all(p.name in NAMES for p in CODE_PERTURBATIONS)

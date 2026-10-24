import pytest

from autograde.ocr import noisy, noisy_items
from autograde.ocr.transcribe import parse
from autograde.schemas import Item

TEXT = (
    "The rate of reaction depends on the concentration of the reactants, and a catalyst "
    "lowers the activation energy. For water, H2O has a bent shape; area is x^2 cm^-1. "
    "Molecular collisions need enough energy to overcome the barrier."
) * 4


def damage(a: str, b: str) -> int:
    """Number of differing positions plus length difference."""
    return sum(x != y for x, y in zip(a, b, strict=False)) + abs(len(a) - len(b))


def test_same_seed_same_output():
    assert noisy(TEXT, "medium", 3) == noisy(TEXT, "medium", 3)
    assert noisy(TEXT, "medium", 3) != noisy(TEXT, "medium", 4)


def test_levels_increase_damage():
    d = {lv: sum(damage(TEXT, noisy(TEXT, lv, s)) for s in range(10)) for lv in LEVELS3}
    assert d["light"] < d["medium"] < d["heavy"]


LEVELS3 = ("light", "medium", "heavy")


def test_math_symbols_lost():
    assert "^" not in noisy("area is x^2 and y^-1 here now", "heavy", 0)


def test_empty_and_bad_level():
    assert noisy("", "heavy", 1) == ""
    assert noisy("   ", "light", 1) == "   "
    with pytest.raises(ValueError):
        noisy("x", "extreme", 0)


def test_items_only_student_answer_changes():
    item = Item(
        id="1", dataset="d", question_id="q", question="Why?", model_answer=TEXT,
        student_answer=TEXT, max_mark=2.0, human_mark=1.0,
    )  # fmt: skip
    (out,) = noisy_items([item], "heavy", 0)
    assert out.student_answer != item.student_answer
    assert (out.question, out.model_answer, out.human_mark) == (
        item.question, item.model_answer, item.human_mark,
    )  # fmt: skip
    assert item.student_answer == TEXT


def test_parse_low_confidence_spans():
    t = parse("The [?enthalpy?] of [?] mixing")
    assert t.low_confidence == ["enthalpy", "?"]

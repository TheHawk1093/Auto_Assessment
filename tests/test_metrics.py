import pytest

from autograde.evaluation.metrics import level, pearson, quadratic_weighted_kappa, report, summarise
from autograde.schemas import Item, Result


def result(pred, human, max_mark=2.0):
    item = Item(id=f"i{pred}{human}", dataset="d", question_id="q", question="q", model_answer="m",
                student_answer="s", max_mark=max_mark, human_mark=human)  # fmt: skip
    return Result(item=item, mode="baseline", predicted_mark=pred)


def test_level_scales_to_five_steps():
    assert [level(m, 2) for m in (0, 0.5, 1, 1.5, 2)] == [0, 1, 2, 3, 4]
    assert level(5, 5) == 4


def test_perfect_agreement():
    s = summarise([result(0, 0), result(1, 1), result(2, 2)])
    assert s["mean_abs_error"] == 0 and s["bias"] == 0
    assert s["same_level"] == 1 and s["qwk"] == pytest.approx(1)


def test_bias_sign_means_generous():
    s = summarise([result(2, 1), result(1, 0)])
    assert s["bias"] == pytest.approx(0.5)


def test_pearson_degenerate_cases_return_none():
    assert pearson([1.0], [1.0]) is None
    assert pearson([1, 1, 1], [1, 2, 3]) is None


def test_qwk_penalises_far_misses_more():
    near = quadratic_weighted_kappa([0, 1, 2, 3, 4], [0, 1, 2, 4, 4])
    far = quadratic_weighted_kappa([0, 1, 2, 3, 4], [4, 1, 2, 3, 0])
    assert near > far


def test_report_splits_by_band_and_ignores_unlabelled():
    rs = [result(0, 0), result(1, 1), result(2, 2), result(2, None)]
    out = report(rs)
    assert out["overall"]["n"] == 3
    assert {k: v["n"] for k, v in out["by_band"].items()} == {"low": 1, "mid": 1, "high": 1}

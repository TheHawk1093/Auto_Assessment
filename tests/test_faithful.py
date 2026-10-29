import pytest

from autograde.ocr.faithful import (
    CASES,
    FONT_DIR,
    SCRIPT_FONTS,
    Case,
    norm,
    render,
    run,
    summarise,
    verdict,
)


def test_a_kept_mistake_is_faithful_and_a_repaired_one_is_not():
    assert verdict("A stack works on the FIFO principle.", "FIFO", "LIFO") == "kept"
    assert verdict("A stack works on the LIFO principle.", "FIFO", "LIFO") == "corrected"
    assert verdict("A stack works on the principle.", "FIFO", "LIFO") == "garbled"


def test_comparison_ignores_spacing_case_and_symbol_variants():
    assert norm("2 × 3 = 7") == norm("2 x 3=7")
    assert verdict("V = I R = 2 A x 5 ohm = 10 A", "10a", "10v") == "kept"
    assert verdict("area = 2πr", "2pir", "pir^2") == "kept"


def test_every_case_has_a_mistake_that_differs_from_the_right_form():
    assert len(CASES) >= 40
    for case in CASES:
        for wrong, right in case.mistakes:
            assert norm(wrong) != norm(right)
            assert norm(wrong) in norm(case.text), case.text


def test_run_scores_a_reader_that_repairs_everything(tmp_path):
    cases = (Case("A stack works on the FIFO principle.", (("FIFO", "LIFO"),)),)
    fonts_there = all((FONT_DIR / f).exists() for f in SCRIPT_FONTS)
    if not fonts_there:
        pytest.skip("handwriting-style fonts are not installed")
    out = run(lambda path, system: "A stack works on the LIFO principle.", "s", tmp_path, cases)
    assert out["corrected"] == 1.0 and out["kept"] == 0.0


def test_summary_of_nothing_is_empty_not_a_crash():
    assert summarise([]) == {"n": 0, "kept": None, "corrected": None, "garbled": None}


def test_rendering_makes_a_png(tmp_path):
    if not (FONT_DIR / SCRIPT_FONTS[0]).exists():
        pytest.skip("handwriting-style fonts are not installed")
    path = render(Case("x + 3 = 7\nx = 7 + 3 = 10", (("7+3=10", "7-3=4"),)), tmp_path / "a.png")
    assert path.exists() and path.stat().st_size > 500

from pathlib import Path

from autograde.config import ReaderConfig, ReaderRoute, Settings, load_settings
from autograde.llm import LLMError
from autograde.ocr.readers import Reader, classify, read_routed, read_with_fallback
from autograde.ocr.sheets import Sheet, SheetItem


def _sheet(name: str) -> Sheet:
    return Sheet(sheet=name, items=[SheetItem(question_id="1", student_answer="x")])


def _failing(_name: str, _pages: list[Path]) -> Sheet:
    raise LLMError("rate limited")


def test_first_reader_that_works_is_used_and_recorded():
    readers = [Reader("a:bad", _failing), Reader("b:good", lambda n, p: _sheet(n))]
    sheet = read_with_fallback(readers, "S_p1", [])
    assert sheet is not None and sheet.reader == "b:good"


def test_later_readers_are_not_called_after_a_success():
    calls = []
    readers = [
        Reader("a:good", lambda n, p: _sheet(n)),
        Reader("b:unused", lambda n, p: calls.append(n) or _sheet(n)),
    ]
    assert read_with_fallback(readers, "S_p1", []).reader == "a:good"
    assert calls == []


def test_all_readers_failing_gives_none():
    assert (
        read_with_fallback([Reader("a:bad", _failing), Reader("b:bad", _failing)], "S", []) is None
    )


def test_default_reader_is_a_free_gemini_model():
    assert Settings().ocr.reader.model == "gemini-3.5-flash-lite"
    assert Settings().ocr.fallbacks == []


def test_example_config_has_a_fallback_chain_and_separate_marker():
    cfg = load_settings(Path("configs/ocr_free.yaml"))
    chain = [cfg.ocr.reader, *cfg.ocr.fallbacks]
    assert [r.provider for r in chain] == ["gemini", "gemini", "gemini", "openrouter", "claude_cli"]
    assert cfg.llm.backend == "goedel"  # marking uses a different model from reading


def _text_sheet(text: str) -> Sheet:
    return Sheet(sheet="S", items=[SheetItem(question_id="1", student_answer=text)])


def test_classify_tells_german_prose_from_matrices_and_english():
    german = (
        "Die Matrix ist nicht diagonalisierbar, weil der Eigenwert mit einer Vielfachheit von zwei"
    )
    assert classify(_text_sheet(german)) == {"german"}
    assert classify(_text_sheet("A = [[1 2 3],[4 5 6]] , λ_1 = -2 , x(t) = e^{-2t} + 3")) == {
        "math"
    }
    assert (
        classify(_text_sheet("The process is stationary because the mean does not depend on time"))
        == set()
    )


def test_route_rereads_matching_kind_and_keeps_first_read_if_specialist_fails():
    route = ReaderRoute(when="math", reader=ReaderConfig())
    maths = _text_sheet("A = [[1 2 3],[4 5 6]] , λ_1 = -2 , x(t) = e^{-2t} + 3")
    first = [Reader("a:main", lambda n, p: maths)]
    good = (route, Reader("b:math", lambda n, p: _text_sheet("[[1 2 3],[4 5 6]]")))
    assert read_routed(first, [good], "S", []).reader == "b:math"
    bad = (route, Reader("b:math", _failing))
    assert read_routed(first, [bad], "S", []).reader == "a:main"
    other = (ReaderRoute(when="german", reader=ReaderConfig()), good[1])
    assert read_routed(first, [other], "S", []).reader == "a:main"


def test_a_blank_read_counts_as_a_failure_and_the_next_reader_is_tried():
    readers = [
        Reader("a:blank", lambda n, p: _text_sheet("  ")),
        Reader("b:good", lambda n, p: _sheet(n)),
    ]
    assert read_with_fallback(readers, "S", []).reader == "b:good"

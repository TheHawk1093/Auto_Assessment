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


def _read(text: str, unsure: int = 0) -> Sheet:
    items = [SheetItem(question_id="1", student_answer=text, unsure=["?"] * unsure)]
    return Sheet(sheet="S", items=items)


def test_empty_page_falls_through_to_the_next_reader():
    readers = [Reader("a:blank", lambda n, p: _read("")), Reader("b:ok", lambda n, p: _read("hi"))]
    assert read_with_fallback(readers, "S", []).reader == "b:ok"


def test_any_exception_not_only_llm_errors_falls_through():
    def boom(_n, _p):
        raise ConnectionResetError("dropped")

    readers = [Reader("a:boom", boom), Reader("b:ok", lambda n, p: _read("hi"))]
    assert read_with_fallback(readers, "S", []).reader == "b:ok"


def test_a_mostly_unsure_read_is_passed_over_for_a_clean_one():
    unsure = _read("one two three four five six", unsure=4)
    readers = [Reader("a:unsure", lambda n, p: unsure), Reader("b:ok", lambda n, p: _read("hi"))]
    assert read_with_fallback(readers, "S", []).reader == "b:ok"


def test_a_looping_reader_is_passed_over():
    loop = _read("the " * 30)
    readers = [Reader("a:loop", lambda n, p: loop), Reader("b:ok", lambda n, p: _read("hi"))]
    assert read_with_fallback(readers, "S", []).reader == "b:ok"


def test_when_no_read_is_clean_the_least_doubtful_is_kept_and_marked():
    worse = _read("a b c d e f", unsure=5)
    better = _read("a b c d e f", unsure=2)
    readers = [Reader("a:worse", lambda n, p: worse), Reader("b:better", lambda n, p: better)]
    sheet = read_with_fallback(readers, "S", [])
    assert sheet is not None and sheet.reader == "b:better (degraded)"


def test_bodhan_reader_sends_images_and_stops_at_its_spend_cap(monkeypatch, tmp_path):
    import pytest

    from autograde.ocr import hosted

    sent = []
    monkeypatch.setattr(hosted, "_key", lambda name: "k")
    monkeypatch.setattr(
        hosted,
        "_call",
        lambda url, headers, body: (
            sent.append((url, body)) or {"choices": [{"message": {"content": "नमस्ते"}}]}
        ),
    )
    monkeypatch.setattr(hosted, "_bodhan_spent", {"images": 0})
    page = tmp_path / "p1.jpeg"
    page.write_bytes(b"\xff\xd8\xff")
    assert hosted.bodhan([page], "indic-ocr", "sys", "user") == "नमस्ते"
    url, body = sent[0]
    assert url == hosted.BODHAN_URL and body["model"] == "indic-ocr"
    assert body["messages"][0]["content"][1]["type"] == "image_url"
    monkeypatch.setattr(hosted, "_bodhan_spent", {"images": 10_000})
    with pytest.raises(LLMError, match="spend"):
        hosted.bodhan([page], "indic-ocr", "sys", "user")


def test_indic_pages_are_recognised_by_script_and_latin_pages_never_are():
    assert "indic" in classify(_text_sheet("नमस्ते दुनिया यह एक परीक्षा है"))
    assert "indic" in classify(_text_sheet("வணக்கம் உலகம் இது ஒரு தேர்வு"))
    assert "indic" in classify(_text_sheet("আমার সোনার বাংলা আমি তোমায় ভালবাসি"))
    assert "indic" not in classify(_text_sheet("Data pre-processing is a step of data analysis"))
    assert "indic" not in classify(_text_sheet("Die Matrix ist nicht diagonalisierbar, weil der"))

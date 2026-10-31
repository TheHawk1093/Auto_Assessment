"""Reading a sheet: tables from a document parser become plain lines; Indic pages are spotted."""

from autograde.ocr.answersheet import _plain, looks_indic


def test_a_parsers_html_table_becomes_lines_of_words():
    html = "<table><tbody><tr><td>one</td><td>two</td></tr><tr><td>three</td></tr></tbody></table>"
    assert _plain(html) == "one two\nthree"


def test_plain_text_is_left_alone():
    assert _plain("Q1. a < b and c > d") == "Q1. a < b and c > d"


def test_a_devanagari_page_is_indic_and_an_english_one_is_not():
    assert looks_indic("आंखों में धूल चली जाने पर आंसू क्यों आ जाते हैं")
    assert not looks_indic("Q1. Define supervised learning.")

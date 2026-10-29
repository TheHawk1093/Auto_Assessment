from autograde.pipeline.codecheck import (
    code_notes,
    extract_code,
    is_python,
    run_tests,
    syntax_report,
)
from autograde.pipeline.figure import FigureDescription, describe_figure, figure_notes
from autograde.schemas import Item


def test_a_model_that_returns_objects_instead_of_strings_is_still_understood():
    fd = FigureDescription.model_validate(
        {"kind": "circuit", "elements": [{"type": "resistor", "position": "top"}, "battery"]}
    )
    assert fd.elements == ["type: resistor; position: top", "battery"]
    assert "Elements: type: resistor; position: top; battery" in fd.render()


def test_the_description_reaches_the_marker_with_a_warning_that_it_is_not_the_image():
    reply = '{"kind": "graph", "elements": ["x axis"], "labels": ["time (s)"], "legible": false}'
    item = Item(
        id="i", dataset="d", question_id="q", question="Sketch v against t.", model_answer="m",
        student_answer="", max_mark=2, kind="diagram", figures=["a.png"],
    )  # fmt: skip
    text, flags = figure_notes(item, lambda pages, system, user: reply)
    assert "you cannot see the image" in text and "time (s)" in text
    assert flags == ["figure_from_description", "figure_unclear"]


def test_a_garbled_reply_is_reported_not_raised():
    item = Item(
        id="i", dataset="d", question_id="q", question="Draw it.", model_answer="m",
        student_answer="", max_mark=2, kind="diagram", figures=["a.png"],
    )  # fmt: skip
    text, flags = figure_notes(item, lambda pages, system, user: "no json here")
    assert flags == ["figure_not_checked"] and "Do not credit" in text
    assert describe_figure  # imported for the real path


def test_fenced_code_is_extracted_and_plain_text_is_kept():
    assert extract_code("Here:\n```python\nx = 1\n```\nDone") == "x = 1"
    assert extract_code("x = 1") == "x = 1"


def test_python_is_recognised_and_other_languages_are_not_checked():
    assert is_python("Write a Python function", "def f(): pass")
    assert not is_python("Write a Java method", "public int f() { return 1; }")


def test_syntax_facts_are_stated_and_hedged_for_handwriting():
    assert "parses" in syntax_report("x = 1")
    bad = syntax_report("def f(x)\n    return x")
    assert "line 1" in bad and "reading mistake" in bad


def test_tests_are_not_run_unless_execution_is_on():
    item = Item(
        id="i", dataset="d", question_id="q", question="Write a Python function f.",
        model_answer="m", student_answer="def f(x):\n    return x + 1", max_mark=2, kind="code",
        tests="assert f(1) == 2\nassert f(0) == 1",
    )  # fmt: skip
    text, flags = code_notes(item, execute=False)
    assert "not run" in text and flags == []


def test_the_teachers_tests_run_in_a_child_process_when_execution_is_on():
    good = run_tests(
        "def f(x):\n    return x + 1", "assert f(1) == 2\nassert f(0) == 1", sandbox="process"
    )
    assert good.ran and (good.passed, good.total) == (2, 2)
    mixed = run_tests(
        "def f(x):\n    return x + 2", "assert f(1) == 2\nassert f(0) == 2", sandbox="process"
    )
    assert (mixed.passed, mixed.total) == (1, 2) and "assert f(1) == 2" in mixed.failed[0]


def test_code_that_hangs_or_crashes_cannot_take_the_run_down():
    loop = run_tests("while True:\n    pass", "assert True", sandbox="process")
    assert loop.error.startswith("timed out")
    crash = run_tests("raise ValueError('boom')", "assert True", sandbox="process")
    assert "ValueError" in crash.error

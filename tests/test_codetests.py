from autograde.pipeline.codecheck import code_notes, outside_imports
from autograde.pipeline.codetests import Drafted, generate_tests
from autograde.schemas import Item
from fakes import FakeClient

QUESTION = "Write a Python function double(x) that returns twice x."


def item(
    answer="def double(x):\n    return 2 * x", tests="", model="def double(x):\n    return x * 2"
):
    return Item(
        id="i", dataset="d", question_id="q", question=QUESTION, model_answer=model,
        student_answer=answer, max_mark=4, kind="code", tests=tests,
    )  # fmt: skip


def test_third_party_imports_are_found_and_the_standard_library_is_not():
    code = (
        "import numpy as np\nfrom pandas import DataFrame\nimport os.path\nfrom json import loads"
    )
    assert outside_imports(code) == ["numpy", "pandas"]
    assert outside_imports("def f(:") == []


def test_code_that_needs_numpy_is_not_run_in_the_wasm_sandbox_and_says_so():
    student = item(
        "import numpy as np\ndef double(x):\n    return np.multiply(x, 2)", "assert double(2) == 4"
    )
    text, flags = code_notes(student, execute=True, sandbox="wasm")
    assert "numpy" in text and "judge by reading" in text and flags == ["code_needs:numpy"]


def test_generated_tests_that_the_reference_fails_are_dropped():
    drafted = Drafted(
        reference="def double(x):\n    return 2 * x",
        tests=[
            "assert double(2) == 4",
            "assert double(0) == 0",
            "assert double(3) == 7",
            "print(1)",
        ],
    )
    client = FakeClient({Drafted: lambda _: drafted.model_dump()})
    kept = generate_tests(item(), client, sandbox="process")
    assert kept.splitlines() == ["assert double(2) == 4", "assert double(0) == 0"]


def test_fewer_than_two_good_tests_means_no_tests():
    drafted = Drafted(reference="def double(x):\n    return 2 * x", tests=["assert double(2) == 5"])
    client = FakeClient({Drafted: lambda _: drafted.model_dump()})
    assert generate_tests(item(), client, sandbox="process") == ""


def test_generated_tests_are_cached_per_question(tmp_path):
    drafted = Drafted(reference="", tests=["assert double(2) == 4", "assert double(1) == 2"])
    client = FakeClient({Drafted: lambda _: drafted.model_dump()})
    first = generate_tests(item(), client, "process", tmp_path)
    again = generate_tests(item(), client, "process", tmp_path)
    assert first == again != "" and client.count(Drafted) == 1


def test_tests_written_by_the_model_are_flagged_in_the_result():
    student = item(tests="assert double(2) == 4\nassert double(5) == 10").model_copy(
        update={"tests_generated": True}
    )
    _, flags = code_notes(student, execute=True, sandbox="process")
    assert "code_tests:2/2" in flags and "tests_generated" in flags

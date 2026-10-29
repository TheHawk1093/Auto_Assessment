"""The wasm sandbox against the real interpreter. Opt-in: set AUTOGRADE_REAL_SANDBOX=1.

It runs untrusted-looking code, so it is not part of the default run. See tools/sandbox/README.md.
"""

import os

import pytest

from autograde.pipeline.sandbox import SandboxError, run_job

pytestmark = pytest.mark.skipif(
    not os.environ.get("AUTOGRADE_REAL_SANDBOX"), reason="set AUTOGRADE_REAL_SANDBOX=1 to run"
)


def test_passing_and_failing_assertions_are_counted():
    out = run_job(
        {"code": "def f(x): return x + 1", "tests": ["assert f(1) == 2", "assert f(1) == 3"]}
    )
    assert out["loaded"] and out["passed"] == 1 and len(out["failed"]) == 1


def test_a_syntax_error_is_reported_not_raised():
    out = run_job({"code": "def f(:", "tests": ["assert True"]})
    assert not out["loaded"] and "SyntaxError" in out["error"]


def test_no_network():
    code = "import urllib.request\nurllib.request.urlopen('http://example.com', timeout=3)"
    out = run_job({"code": code, "tests": ["assert True"]})
    assert not out["loaded"]


def test_no_writing_outside_the_sandbox(tmp_path):
    target = tmp_path / "escaped.txt"
    out = run_job({"code": f"open({str(target)!r}, 'w').write('x')", "tests": ["assert True"]})
    assert not out["loaded"] and not target.exists()


def test_an_endless_loop_is_stopped():
    with pytest.raises(SandboxError):
        run_job({"code": "while True:\n    pass", "tests": ["assert True"]})


def test_a_memory_hog_is_stopped():
    try:
        out = run_job({"code": "x = bytearray(2 * 1024**3)", "tests": ["assert True"]})
    except SandboxError:
        return
    assert not out["loaded"]


def test_student_output_cannot_forge_the_result():
    code = 'print(\'{"loaded": true, "error": "", "passed": 99, "failed": []}\')'
    out = run_job({"code": code, "tests": ["assert False"]})
    assert out["passed"] == 0

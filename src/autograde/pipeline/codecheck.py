"""Code answers: what code can establish before a model judges the rest.

By default nothing the student wrote is run. Code checks give the marker facts it cannot see by
reading (does it even parse?) and the marker judges logic against the rubric. Running the
student's program against the teacher's tests is available but off: it executes untrusted code,
so it runs only in the sandbox (`pipeline/sandbox.py`), and handwritten code read by OCR
rarely survives a literal run (one misread character is a syntax error). When it is on, only
the tests are run, with a time limit.
"""

from __future__ import annotations

import ast
import re
import sys
from dataclasses import dataclass, field

from autograde.pipeline.sandbox import SandboxError, run_job
from autograde.schemas import Item

FENCE = re.compile(r"```[A-Za-z0-9+#_-]*\n(.*?)```", re.S)
PYTHON_HINT = re.compile(
    r"\bpython\b|\bdef \w+\(|\bimport \w+|\bprint\(|\bself\b|:\s*$", re.I | re.M
)
OTHER_LANGUAGES = re.compile(
    r"\b(java|c\+\+|c#|javascript|matlab|verilog|vhdl|assembly|sql)\b", re.I
)


@dataclass
class TestRun:
    """Outcome of running the teacher's tests on a student's code.

    Attributes:
        ran: Whether the tests ran at all.
        passed: Number of tests that passed.
        total: Number of tests run.
        failed: The failing test lines.
    """

    __test__ = False  # not a pytest class
    ran: bool
    passed: int = 0
    total: int = 0
    failed: list[str] = field(default_factory=list)
    error: str = ""
    unrun: bool = False  # the sandbox could not start: nothing was learned about the code


def extract_code(answer: str) -> str:
    """The code in an answer: the fenced blocks if there are any, else the whole text."""
    blocks = FENCE.findall(answer)
    return "\n".join(b.strip("\n") for b in blocks) if blocks else answer.strip()


def is_python(question: str, code: str) -> bool:
    """Say whether the question and code look like Python rather than another language."""
    if OTHER_LANGUAGES.search(question):
        return False
    return bool(PYTHON_HINT.search(question + "\n" + code))


def syntax_report(code: str) -> str:
    """A one-line fact about whether the code parses (Python only)."""
    try:
        ast.parse(code)
    except SyntaxError as exc:
        return (
            f"Python syntax error at line {exc.lineno}: {exc.msg}. If this answer was read from "
            "handwriting, this may be a reading mistake, not the student's."
        )
    return "Python syntax check: the code parses."


def outside_imports(code: str) -> list[str]:
    """List top-level imports outside the standard library (numpy, pandas...).

    The WebAssembly interpreter has only the standard library, so such code cannot be run there.
    """
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            found.add(node.module.split(".")[0])
    return sorted(m for m in found if m not in sys.stdlib_module_names)


def run_tests(code: str, tests: str, sandbox: str = "wasm") -> TestRun:
    """Run the teacher's tests (one `assert` per line) against the code in the sandbox.

    See `pipeline/sandbox.py`. Off by default; see the module note on safety.
    """
    lines = [t for t in tests.splitlines() if t.strip()]
    if not lines:
        return TestRun(False)
    try:
        data = run_job({"code": code, "tests": lines}, sandbox)
    except SandboxError as exc:
        timed_out = "timed out" in str(exc)  # an endless loop is the code's fault, not ours
        return TestRun(True, 0, len(lines), error=str(exc), unrun=not timed_out)
    if not data["loaded"]:
        return TestRun(True, 0, len(lines), error=data["error"])
    return TestRun(True, data["passed"], len(lines), data["failed"])


def code_notes(item: Item, execute: bool, sandbox: str = "wasm") -> tuple[str, list[str]]:
    """Facts for the marker about a code answer, and flags for the teacher."""
    code = extract_code(item.student_answer)
    if not code:
        return "", []
    if not is_python(item.question, code):
        return "The language is not Python, so the code was not checked automatically.", []
    lines, flags = [syntax_report(code)], []
    if lines[0].startswith("Python syntax error"):
        flags.append("code_syntax_error")
    outside = outside_imports(code) if sandbox == "wasm" else []
    if execute and item.tests.strip() and outside:
        lines.append(
            f"The code uses {', '.join(outside)}, which the safe sandbox does not have, so the "
            "teacher's tests were not run; judge by reading."
        )
        flags.append(f"code_needs:{','.join(outside)}")
    elif execute and item.tests.strip() and not flags:
        run = run_tests(code, item.tests, sandbox)
        if run.unrun:
            lines.append(f"The teacher's tests could not be run ({run.error}); judge by reading.")
            flags.append("code_not_run")
        elif run.error:
            lines.append(f"The student's code failed when run: {run.error}.")
            flags.append("code_run_error")
        else:
            lines.append(
                f"The teacher's tests were run on the code: {run.passed} of {run.total} passed."
            )
            lines += [f"  failed: {f}" for f in run.failed[:3]]
            flags.append(f"code_tests:{run.passed}/{run.total}")
            if item.tests_generated:
                flags.append("tests_generated")
    elif item.tests.strip():
        lines.append("The teacher's tests were not run (execution is off); judge by reading.")
    return "\n".join(lines), flags

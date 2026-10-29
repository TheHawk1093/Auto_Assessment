"""Tests for a code question that came without any.

The model writes a reference solution and one-line asserts from the question and the teacher's
model answer. A test is kept only if the reference solution passes it when run in the sandbox, so
a wrong or ill-posed test (the usual failure of generated tests) never reaches a student's mark.
Fewer than two surviving tests means no tests: the answer is then judged by reading, as before.
The result is cached per question, and every item that uses it is flagged `tests_generated`.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

from pydantic import BaseModel, Field

from autograde import prompts
from autograde.llm import LLMClient
from autograde.pipeline.codecheck import extract_code, outside_imports
from autograde.pipeline.sandbox import SandboxError, run_job
from autograde.schemas import Item

log = logging.getLogger(__name__)
MIN_TESTS = 2


class Drafted(BaseModel):
    reference: str = Field(description="A correct standard-library Python solution.")
    tests: list[str] = Field(description="One line each: an assert on the student's code.")


def _key(item: Item, n: int) -> str:
    text = f"{item.question}\n{item.model_answer}\n{n}"
    return hashlib.sha1(text.encode()).hexdigest()[:12]


def generate_tests(
    item: Item, client: LLMClient, sandbox: str, cache: Path | None = None, n: int = 6
) -> str:
    """Validated tests as text, one assert per line; empty when none could be trusted."""
    path = cache / f"{_key(item, n)}.json" if cache else None
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["tests"]
    user = (
        f"Question:\n{item.question}\n\n"
        f"Teacher's model answer:\n{item.model_answer or '(none)'}\n\n"
        f"Write up to {n} tests."
    )
    drafted = client.ask(prompts.system("codetests"), user, Drafted)
    lines = [t.strip() for t in drafted.tests if t.strip().startswith("assert")][:n]
    reference = extract_code(item.model_answer) if "def " in item.model_answer else ""
    reference = reference or extract_code(drafted.reference)
    kept: list[str] = []
    if lines and reference and not outside_imports(reference):
        try:
            data = run_job({"code": reference, "tests": lines}, sandbox)
        except SandboxError as exc:
            log.warning("Generated tests for %s were not validated: %s", item.question_key, exc)
            return ""  # not cached: a later run with a working sandbox may succeed
        if data["loaded"]:
            failed = {f.split("  -> ")[0] for f in data["failed"]}
            kept = [t for t in lines if t[:120] not in failed]
    tests = "\n".join(kept) if len(kept) >= MIN_TESTS else ""
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"tests": tests, "dropped": len(lines) - len(kept)}), "utf-8")
    return tests

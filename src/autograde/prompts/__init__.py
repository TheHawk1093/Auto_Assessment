"""Prompt templates, one markdown file each, grouped by stage in the folders next to this module.

A name is the file name without `.md` and is unique across folders, so call sites never mention a
folder: `rubric/` the scheme writer, `grade/` the marker, `read/` the first pass, `feedback/` the
feedback writers, `language/` everything specific to a language other than English (feedback
register per language, translation), `intake/` teacher files, `ocr/` handwriting, `checks/` the
code, figure and transcription helpers, `eval/` the judge and the extra tests.

Templates use `{name}` placeholders filled by `str.format`, so they contain no other braces.
"""

from __future__ import annotations

from functools import cache
from importlib import resources
from importlib.resources.abc import Traversable


@cache
def _index() -> dict[str, Traversable]:
    root = resources.files(__package__)
    return {
        path.name: path
        for folder in root.iterdir()
        if folder.is_dir() and not folder.name.startswith("__")
        for path in folder.iterdir()
        if path.name.endswith(".md")
    }


def files() -> dict[str, Traversable]:
    """Every prompt file by file name (with `.md`)."""
    return _index()


@cache
def _read(name: str) -> str:
    try:
        return _index()[f"{name}.md"].read_text(encoding="utf-8")
    except KeyError:
        raise FileNotFoundError(f"no prompt named {name!r}") from None


def render(name: str, **values: object) -> str:
    """Return the named prompt with its placeholders filled from `values`."""
    return _read(name).format(**values).strip()


def system(name: str) -> str:
    """Return the named stage's system prompt."""
    return _read(f"{name}.system").strip()


def optional(name: str) -> str:
    """A system prompt part that may not exist yet (per answer type or per field): else empty."""
    try:
        return system(name)
    except FileNotFoundError:
        return ""

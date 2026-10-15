"""Prompt templates stored as markdown files next to this module.

Templates use `{name}` placeholders filled by `str.format`, so they contain no other braces.
"""

from __future__ import annotations

from functools import cache
from importlib import resources


@cache
def _read(name: str) -> str:
    return resources.files(__package__).joinpath(f"{name}.md").read_text(encoding="utf-8")


def render(name: str, **values: object) -> str:
    return _read(name).format(**values).strip()


def system(name: str) -> str:
    return _read(f"{name}.system").strip()

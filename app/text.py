"""Text clean-up shared by the services and the UI: Unicode forms and maths delimiters.

Indic scripts (and accented Latin) have more than one way to encode the same word. Windows and
macOS even disagree on file names inside a zip. Everything that enters the app, or is shown, is
brought to NFC so the same word is always the same string. The joiners U+200C and U+200D are
kept: they change how conjuncts look. (The marking backend drops them only when it compares
quotes, `pipeline/verify._unicode`.)
"""

from __future__ import annotations

import re
import unicodedata

_BLOCK = re.compile(r"\\\[(.+?)\\\]", re.DOTALL)
_INLINE = re.compile(r"\\\((.+?)\\\)", re.DOTALL)
_MATH = re.compile(r"\$\$.+?\$\$|\$[^$\n]+?\$", re.DOTALL)
_MD_CHARS = re.compile(r"([\\`*_{}\[\]<>#|~])")


def normalize(text: str) -> str:
    """NFC, no byte-order mark, no stray control characters (tabs and newlines stay)."""
    text = unicodedata.normalize("NFC", text).replace("﻿", "")
    return "".join(c for c in text if c in "\t\n\r" or unicodedata.category(c) != "Cc")


def for_markdown(text: str) -> str:
    r"""Prepare text for Streamlit's markdown, converting `\(..\)` and `\[..\]` maths.

    Streamlit renders `$..$` and `$$..$$` with KaTeX, but not `\(..\)` or `\[..\]`, which models
    and teachers often write. Those are converted, and the rest is normalised.
    """
    text = normalize(text)
    text = _BLOCK.sub(lambda m: f"$${m.group(1)}$$", text)
    return _INLINE.sub(lambda m: f"${m.group(1)}$", text)


def plain_for_markdown(text: str) -> str:
    """Plain text (an answer, feedback) as markdown that keeps maths and line breaks.

    Maths between dollar signs is kept so Streamlit draws it; everything else is escaped so a
    `*`, `_` or `#` in someone's writing stays as written.
    """
    text = for_markdown(text).strip()
    out, last = [], 0
    for m in _MATH.finditer(text):
        out.append(_escape(text[last : m.start()]))
        out.append(m.group(0))
        last = m.end()
    out.append(_escape(text[last:]))
    return "".join(out)


def _escape(part: str) -> str:
    return _MD_CHARS.sub(lambda m: "\\" + m.group(1), part).replace("\n", "  \n")

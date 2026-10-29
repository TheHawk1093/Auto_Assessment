"""Figures inside answer and reference files.

A student draws a circuit, a graph or a diagram; the file holds it as a markdown image
(`![](fig1.png)`), a `[figure: fig1.png]` line, or, in a .docx, as an embedded picture. When a file
is read, each such reference is rewritten to the absolute path of the image so it survives the
splitting of the text per question. `split_figures` then separates the picture paths from the
words when the items are built; the words go to the marker and the pictures to the describer
(`pipeline/figure.py`).
"""

from __future__ import annotations

import re
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}
_MARKDOWN = re.compile(r"!\[[^\]]*\]\(\s*<?([^)>\s]+)>?(?:\s+\"[^\"]*\")?\s*\)")
_TAGGED = re.compile(
    r"^[ \t]*\[(?:figure|fig|image|drawing)\s*:\s*([^\]]+?)\s*\][ \t]*$", re.I | re.M
)
_ANY = re.compile(
    r"!\[[^\]]*\]\([^)]*\)|^[ \t]*\[(?:figure|fig|image|drawing)\s*:[^\]]*\][ \t]*$", re.I | re.M
)


def _is_image(ref: str) -> bool:
    return Path(ref.split("?")[0]).suffix.lower() in IMAGE_SUFFIXES


def anchor_figures(text: str, base: Path) -> str:
    """Rewrite relative image references to absolute paths. A reference to a file that does not
    exist is left as it is, so it is reported later as a missing figure."""

    def fix(ref: str) -> str:
        if not _is_image(ref) or re.match(r"^[a-z]+://", ref):
            return ref
        path = Path(ref)
        path = path if path.is_absolute() else base / path
        return path.resolve().as_posix() if path.exists() else ref

    text = _MARKDOWN.sub(lambda m: f"![]({fix(m.group(1))})", text)
    return _TAGGED.sub(lambda m: f"[figure: {fix(m.group(1).strip())}]", text)


def split_figures(text: str) -> tuple[str, list[str]]:
    """The text without its image references, and the image paths in the order they appear."""
    paths = [m.group(1) for m in _MARKDOWN.finditer(text) if _is_image(m.group(1))]
    paths += [m.group(1).strip() for m in _TAGGED.finditer(text) if _is_image(m.group(1))]
    clean = _ANY.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", clean).strip(), paths


def docx_pictures(zf, xml: str) -> dict[int, list[str]]:
    """Picture file names in a .docx, keyed by the position of the paragraph that holds them."""
    try:
        rels = zf.read("word/_rels/document.xml.rels").decode("utf-8")
    except KeyError:  # a document with no pictures may have no relationships file
        return {}
    target = {
        m.group(1): m.group(2)
        for m in re.finditer(r'<Relationship [^>]*?Id="([^"]+)"[^>]*?Target="([^"]+)"', rels)
    }
    target.update(
        {
            m.group(2): m.group(1)
            for m in re.finditer(r'<Relationship [^>]*?Target="([^"]+)"[^>]*?Id="([^"]+)"', rels)
        }
    )
    found: dict[int, list[str]] = {}
    for i, para in enumerate(re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.DOTALL)):
        embeds = re.findall(r'r:embed="([^"]+)"', para)
        names = [target[e] for e in embeds if e in target and _is_image(target[e])]
        if names:
            found[i] = [f"word/{n.lstrip('/')}".replace("word/word/", "word/") for n in names]
    return found

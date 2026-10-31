"""Shared pieces of the image readers: the image types and the `[?word?]` unsure marker.

Readers (`hosted.py`) return plain text in which unreadable words are marked `[?word?]`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

MEDIA = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
UNSURE = re.compile(r"\[\?([^\]?]*)\??\]")


@dataclass
class Transcript:
    """A transcription and the spans the reader marked unsure."""

    text: str
    low_confidence: list[str] = field(default_factory=list)


def parse(raw: str) -> Transcript:
    """Split the model reply into text and the spans it marked unsure."""
    text = raw.strip()
    return Transcript(text, [m.group(1).strip() or "?" for m in UNSURE.finditer(text)])

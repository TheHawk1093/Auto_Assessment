"""A tiny text-only PDF writer, so the demo can hand the app real PDF files to read.

Plain Helvetica text on A4 pages, with a text layer the reader can extract. Not for general use:
characters outside Latin-1 become '?'.
"""

from __future__ import annotations

import textwrap

WIDTH = 92  # characters per line
LINES = 52  # lines per page


def _escape(line: str) -> bytes:
    raw = line.encode("latin-1", "replace")
    return raw.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)")


def pdf_bytes(text: str) -> bytes:
    """Return a PDF holding the text, wrapped and split over pages."""
    lines: list[str] = []
    for para in text.splitlines():
        lines += textwrap.wrap(para, WIDTH) or [""]
    pages = [lines[i : i + LINES] for i in range(0, len(lines), LINES)] or [[""]]
    objects: list[bytes] = [b"", b"", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
                            b"/Encoding /WinAnsiEncoding >>"]  # 1 catalog, 2 pages, 3 font
    kids = []
    for page in pages:
        body = b"BT /F1 11 Tf 14 TL 50 800 Td\n" + b"".join(
            b"(" + _escape(line) + b") Tj T*\n" for line in page
        ) + b"ET"
        objects.append(b"<< /Length %d >>\nstream\n" % len(body) + body + b"\nendstream")
        content = len(objects)
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents %d 0 R "
            b"/Resources << /Font << /F1 3 0 R >> >> >>" % content
        )
        kids.append(b"%d 0 R" % len(objects))
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"
    objects[1] = b"<< /Type /Pages /Kids [" + b" ".join(kids) + b"] /Count %d >>" % len(kids)
    out = b"%PDF-1.4\n"
    offsets = []
    for number, obj in enumerate(objects, 1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % number + obj + b"\nendobj\n"
    start = len(out)
    out += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objects) + 1)
    out += b"".join(b"%010d 00000 n \n" % o for o in offsets)
    out += b"trailer\n<< /Size %d /Root 1 0 R >>\n" % (len(objects) + 1)
    out += b"startxref\n%d\n%%%%EOF\n" % start
    return out

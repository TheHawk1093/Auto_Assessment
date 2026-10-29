"""Render the scanned answer sheets (PDF) to one image per page, named `<Student>_p<N>.jpeg`.

    .venv-ocr/Scripts/python tools/ocr/pdf_to_pages.py data/raw/mendeley_exam/sheets \
        data/raw/mendeley_exam/pages [--scale 2.0]

Needs pypdfium2, which is in the separate .venv-ocr (not in the main environment). Only the PDFs in
the source folder are rendered, so the sealed benchmark students (never downloaded) stay unseen.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pypdfium2 as pdfium


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("src", type=Path)
    p.add_argument("dst", type=Path)
    p.add_argument("--scale", type=float, default=2.0, help="2.0 is about 144 dpi")
    a = p.parse_args()
    a.dst.mkdir(parents=True, exist_ok=True)
    total = 0
    for pdf in sorted(a.src.glob("*.pdf")):
        doc = pdfium.PdfDocument(str(pdf))
        for n in range(len(doc)):
            out = a.dst / f"{pdf.stem}_p{n + 1}.jpeg"
            if not out.exists():
                doc[n].render(scale=a.scale).to_pil().convert("RGB").save(out, quality=88)
            total += 1
        doc.close()
    print(f"{total} pages in {a.dst}")


if __name__ == "__main__":
    main()

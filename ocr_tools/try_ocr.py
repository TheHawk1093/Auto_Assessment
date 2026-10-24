"""Run the OCR engines on images and save each engine's text for side-by-side reading.

    .venv-ocr/Scripts/python ocr_tools/try_ocr.py data/ocr_images            # all engines
    .venv-ocr/Scripts/python ocr_tools/try_ocr.py page.png --engines got,trocr

Output goes to <folder>/_out/<image>.<engine>.txt, and a timing table is printed.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ocr_engines import ENGINES  # noqa: E402

SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".webp"}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("path", type=Path, help="an image or a folder of images")
    p.add_argument("--engines", default=",".join(ENGINES), help="comma separated")
    args = p.parse_args()
    images = (
        sorted(f for f in args.path.iterdir() if f.suffix.lower() in SUFFIXES)
        if args.path.is_dir()
        else [args.path]
    )
    out_dir = (args.path if args.path.is_dir() else args.path.parent) / "_out"
    out_dir.mkdir(exist_ok=True)
    for image in images:
        for name in args.engines.split(","):
            start = time.time()
            try:
                text = ENGINES[name](image)
            except Exception as exc:  # one failing engine must not stop the others
                text = f"[failed: {exc}]"
            (out_dir / f"{image.stem}.{name}.txt").write_text(text, encoding="utf-8")
            print(f"{image.name:30} {name:9} {time.time() - start:6.1f}s {len(text):6} chars")


if __name__ == "__main__":
    main()

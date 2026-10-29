"""White out the name and roll-number lines on copies of the answer-sheet photos.

    python tools/ocr/redact_headers.py data/OCR_Dataset <out_dir>

Images are copied unchanged unless they have an entry in BOXES. Boxes are (x0, y0, x1, y1) as
fractions of the image size, found by looking at the pages, so check the output before sending
images anywhere. Used before any image leaves this machine.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

import cv2
import numpy as np

BOXES: dict[str, list[tuple[float, float, float, float]]] = {
    "German_p2": [(0.0, 0.0, 1.0, 0.035)],
    "Probab_p1": [(0.0, 0.145, 1.0, 0.195)],
    "Network_dynamics_p1": [(0.0, 0.163, 1.0, 0.193)],
}


def redact(src: Path, dst: Path) -> None:
    boxes = BOXES.get(src.stem)
    if not boxes:
        shutil.copyfile(src, dst)
        return
    img = cv2.imdecode(np.fromfile(str(src), dtype=np.uint8), cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    for x0, y0, x1, y1 in boxes:
        img[int(y0 * h) : int(y1 * h), int(x0 * w) : int(x1 * w)] = 255
    cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 92])[1].tofile(str(dst))


def main(src_dir: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for path in sorted(Path(src_dir).glob("*.jpeg")):
        redact(path, out / path.name)
        print("redacted" if path.stem in BOXES else "copied", path.name)


if __name__ == "__main__":
    main(*sys.argv[1:3])

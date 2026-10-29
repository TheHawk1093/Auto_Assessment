"""Put the handwritten word images of each selected page back together into one page image.

    .venv-ocr/Scripts/python tools/ocr/compose_indic_pages.py data/raw/indic_words

Reads `split.json` (written by `python -m autograde.datasets.handwriting`) and writes, per part
(tune, validate), a folder `pages_<part>/` of `<Language>_<writer>_<page>_p1.jpeg` and a
`truth_<part>.json` with the page's text. The words are real handwriting; only the layout (words
left to right, wrapped into lines, white background) is ours, so this tests reading the script,
not photographed paper. Needs Pillow, which is in the separate .venv-ocr.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

LINE_HEIGHT = 64
WIDTH = 1000
GAP = 18
MARGIN = 24


def whiten(img: Image.Image) -> Image.Image:
    """Ink on white paper: scale each crop so its background (the median grey) becomes white, so
    crops with different tints no longer look like a patchwork figure to a layout parser."""
    grey = img.convert("L")
    background = max(1, sorted(grey.getdata())[len(grey.getdata()) // 2])
    return grey.point(lambda v: min(255, int(v * 255 / background))).convert("RGB")


def compose(words: list[Path], clean: bool = False) -> Image.Image:
    """Words in order, scaled to one height, wrapped into lines."""
    crops = []
    for path in words:
        img = Image.open(path).convert("RGB")
        if clean:
            img = whiten(img)
        crops.append(img.resize((max(1, round(img.width * LINE_HEIGHT / img.height)), LINE_HEIGHT)))
    lines: list[list[Image.Image]] = [[]]
    x = MARGIN
    for crop in crops:
        if x + crop.width > WIDTH - MARGIN and lines[-1]:
            lines.append([])
            x = MARGIN
        lines[-1].append(crop)
        x += crop.width + GAP
    page = Image.new("RGB", (WIDTH, 2 * MARGIN + len(lines) * (LINE_HEIGHT + GAP)), "white")
    for row, line in enumerate(lines):
        x = MARGIN
        for crop in line:
            page.paste(crop, (x, MARGIN + row * (LINE_HEIGHT + GAP)))
            x += crop.width + GAP
    return page


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--clean", action="store_true", help="whiten backgrounds; pages_<part>_clean/")
    args = p.parse_args()
    root = args.root
    manifest = json.loads((root / "split.json").read_text(encoding="utf-8"))
    for part in ("tune", "validate"):
        out = root / f"pages_{part}{'_clean' if args.clean else ''}"
        out.mkdir(exist_ok=True)
        truth = {}
        for language, info in manifest.items():
            for page in info[part]:
                parts = page.split("/")
                name = f"{language}_{parts[-2]}_{parts[-1]}"
                rows = info["words"][page]
                image = compose([root / language / "words" / r["file"] for r in rows], args.clean)
                image.save(out / f"{name}_p1.jpeg", quality=90)
                truth[name] = " ".join(r["text"] for r in rows)
        (root / f"truth_{part}.json").write_text(
            json.dumps(truth, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print(part, len(truth), "pages")


if __name__ == "__main__":
    main()

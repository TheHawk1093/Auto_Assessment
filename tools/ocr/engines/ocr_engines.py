"""Free, open-source OCR engines behind one function each: image path in, text out.

Runs in the separate `.venv-ocr` environment (see requirements.txt). CPU only.
Engines load on first use and are kept, so a folder of images loads each model once.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

import numpy as np
from PIL import Image

TROCR = "microsoft/trocr-base-handwritten"
GOT = "stepfun-ai/GOT-OCR-2.0-hf"


def _lines(image: Image.Image) -> list[Image.Image]:
    """Cut a page into text lines by finding blank horizontal bands (simple, for neat pages)."""
    import cv2

    gray = np.array(image.convert("L"))
    ink = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1] > 0
    rows = ink.sum(axis=1) > max(2, 0.004 * ink.shape[1])
    cuts, start = [], None
    for y, on in enumerate(rows):
        if on and start is None:
            start = y
        elif not on and start is not None:
            if y - start > 12:
                cuts.append((start, y))
            start = None
    if start is not None:
        cuts.append((start, len(rows)))
    pad = 6
    return [
        image.crop((0, max(0, a - pad), image.width, min(image.height, b + pad))) for a, b in cuts
    ] or [image]


@cache
def _easyocr():
    import easyocr

    return easyocr.Reader(["en"], gpu=False, verbose=False)


def easyocr_text(path: Path) -> str:
    """EasyOCR (CRAFT detector + CRNN reader). Good on print, fair on neat handwriting."""
    return "\n".join(_easyocr().readtext(str(path), detail=0, paragraph=True))


@cache
def _rapid():
    from rapidocr_onnxruntime import RapidOCR

    return RapidOCR()


def rapidocr_text(path: Path) -> str:
    """RapidOCR (PaddleOCR models on ONNX). Fast and strong on print, weak on handwriting."""
    result, _ = _rapid()(str(path))
    return "\n".join(r[1] for r in result or [])


@cache
def _doctr():
    from doctr.models import ocr_predictor

    return ocr_predictor(pretrained=True)


def doctr_text(path: Path) -> str:
    """docTR (DBNet detector + CRNN reader). Solid on print and clean scans."""
    from doctr.io import DocumentFile

    doc = _doctr()(DocumentFile.from_images(str(path)))
    return doc.render()


@cache
def _trocr():
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel

    return TrOCRProcessor.from_pretrained(TROCR), VisionEncoderDecoderModel.from_pretrained(TROCR)


def trocr_text(path: Path) -> str:
    """TrOCR handwritten (transformer): the best open handwriting reader here, line by line."""
    processor, model = _trocr()
    out = []
    for line in _lines(Image.open(path).convert("RGB")):
        pixels = processor(images=line, return_tensors="pt").pixel_values
        ids = model.generate(pixels, max_new_tokens=96)
        out.append(processor.batch_decode(ids, skip_special_tokens=True)[0])
    return "\n".join(out)


@cache
def _got():
    from transformers import AutoModelForImageTextToText, AutoProcessor

    return (
        AutoProcessor.from_pretrained(GOT),
        AutoModelForImageTextToText.from_pretrained(GOT),
    )


def got_text(path: Path) -> str:
    """GOT-OCR 2.0 (0.6B vision-language model). Reads whole pages, formulas and tables."""
    processor, model = _got()
    inputs = processor(Image.open(path).convert("RGB"), return_tensors="pt")
    ids = model.generate(**inputs, do_sample=False, max_new_tokens=2048, stop_strings="<|im_end|>",
                         tokenizer=processor.tokenizer)  # fmt: skip
    return processor.decode(ids[0, inputs["input_ids"].shape[1] :], skip_special_tokens=True)


ENGINES = {
    "rapidocr": rapidocr_text,
    "easyocr": easyocr_text,
    "doctr": doctr_text,
    "trocr": trocr_text,
    "got": got_text,
}

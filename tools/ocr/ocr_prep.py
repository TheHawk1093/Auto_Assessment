"""Image preparation for classical OCR: isolate the student's pen ink from print and teacher marks.

Exam photos have three inks: black print (questions), blue or black pen (the student), red pen
(the teacher). Engines read print well and handwriting badly, and the red marks add noise, so the
best input is an image holding only the student's ink.
"""

from __future__ import annotations

import cv2
import numpy as np


def ink_mask(bgr: np.ndarray, hue=(95, 135), sat_min: int = 55, val_min: int = 40) -> np.ndarray:
    """255 where a pixel looks like blue ink. Hue is on OpenCV's 0-179 scale."""
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    return (((h >= hue[0]) & (h <= hue[1]) & (s >= sat_min) & (v >= val_min)) * 255).astype(
        np.uint8
    )


def student_ink(
    bgr: np.ndarray, scale: float = 2.0, close: int = 3, hue=(95, 135), sat_min: int = 55,
    min_blob: int = 6,
) -> np.ndarray:  # fmt: skip
    """Black ink on a white page, upscaled; speckle removed and thin strokes joined."""
    mask = ink_mask(bgr, hue, sat_min)
    if scale != 1:
        mask = cv2.resize(mask, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
        mask = (mask > 127).astype(np.uint8) * 255
    if close:
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((close, close), np.uint8))
    n, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    keep = np.zeros_like(mask)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= min_blob * (scale**2):
            keep[labels == i] = 255
    return 255 - keep


def gray_clahe(bgr: np.ndarray, scale: float = 2.0) -> np.ndarray:
    """Plain grayscale with local contrast, for print-and-handwriting pages read as a whole."""
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    if scale != 1:
        gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)


def prepare(path: str, mode: str, **kw) -> np.ndarray:
    # imdecode so that paths with spaces or non-ASCII characters work on Windows
    bgr = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if mode == "raw":
        return bgr
    if mode == "gray":
        return gray_clahe(bgr, **kw)
    if mode == "ink":
        return student_ink(bgr, **kw)
    raise ValueError(f"unknown prep mode {mode!r}")

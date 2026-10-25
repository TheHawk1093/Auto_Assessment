"""Run classical OCR engines on the answer-sheet photos and score them.

    python tools/ocr_bench.py run  --engine tesseract --prep ink --out runs/ocrb_tess_ink
    python tools/ocr_bench.py tune --engine tesseract            # grid on the dev pages only

Each run writes `<out>/lines.json` ({image: [text lines]}), readable by `autograde.ocr.score`.
Engines live in a separate virtual environment (heavy dependencies), so this file avoids the
autograde package; it loads the stdlib-only metrics module by path.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from ocr_prep import prepare  # noqa: E402

spec = importlib.util.spec_from_file_location("metrics", ROOT / "src/autograde/ocr/metrics.py")
metrics = importlib.util.module_from_spec(spec)
sys.modules["metrics"] = metrics
spec.loader.exec_module(metrics)

IMAGES = ROOT / "data/OCR_Dataset"
TRUTH = json.loads((IMAGES / "truth_pages.json").read_text("utf-8"))
TESSERACT = os.environ.get("TESSERACT", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
TESSDATA = os.environ.get("TESSDATA_PREFIX", "")

_cache: dict = {}


def _png(img: np.ndarray) -> str:
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    cv2.imencode(".png", img)[1].tofile(path)
    return path


def tesseract(img, lang="deu+eng", psm=6, oem=1, dpi=300, **_) -> list[str]:
    path = _png(img)
    try:
        cmd = [TESSERACT, path, "stdout", "-l", lang, "--psm", str(psm), "--oem", str(oem)]
        cmd += ["--dpi", str(dpi)]
        if TESSDATA:
            cmd += ["--tessdata-dir", TESSDATA]
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8").stdout
    finally:
        os.unlink(path)
    return [line for line in out.splitlines() if line.strip()]


def rapidocr(img, text_score=0.5, det_box_thresh=0.5, det_unclip_ratio=1.6, det_limit=736, **_):
    from rapidocr_onnxruntime import RapidOCR

    key = ("rapid", text_score, det_box_thresh, det_unclip_ratio, det_limit)
    if key not in _cache:
        _cache[key] = RapidOCR(
            text_score=text_score,
            det_box_thresh=det_box_thresh,
            det_unclip_ratio=det_unclip_ratio,
            det_limit_side_len=det_limit,
        )
    res, _ = _cache[key](img)
    return [r[1] for r in (res or [])]


def easyocr_run(
    img, langs=("de", "en"), text_threshold=0.7, low_text=0.4, mag_ratio=1.0,
    contrast_ths=0.1, width_ths=0.5, decoder="greedy", **_,
):  # fmt: skip
    import easyocr

    key = ("easy", tuple(langs))
    if key not in _cache:
        _cache[key] = easyocr.Reader(list(langs), gpu=False, verbose=False)
    out = _cache[key].readtext(
        img, detail=0, paragraph=False, text_threshold=text_threshold, low_text=low_text,
        mag_ratio=mag_ratio, contrast_ths=contrast_ths, width_ths=width_ths, decoder=decoder,
    )  # fmt: skip
    return list(out)


ENGINES = {"tesseract": tesseract, "rapidocr": rapidocr, "easyocr": easyocr_run}


def register(name: str):
    def wrap(fn):
        ENGINES[name] = fn
        return fn

    return wrap


def read_all(engine: str, prep: str, prep_kw: dict, eng_kw: dict, pages=None) -> dict:
    out = {}
    for path in sorted(IMAGES.glob("*.jpeg")):
        if pages and path.stem not in pages:
            continue
        img = prepare(str(path), prep, **prep_kw)
        out[path.name] = ENGINES[engine](img, **eng_kw)
    return out


def score_lines(lines: dict, split: str | None = None) -> dict:
    """Mean recall / fuzzy recall / fact score over truth pages (dev or test), plus tokens read."""
    rows = []
    for name, t in TRUTH.items():
        if name.startswith("_") or (split and t["split"] != split):
            continue
        text = " ".join(lines.get(f"{name}.jpeg", []))
        r = {"recall": None, "fuzzy": None, "facts": None, "precision": None}
        if "tokens" in t:
            r["recall"] = metrics.recall(t["tokens"], text)
            r["fuzzy"] = metrics.recall(t["tokens"], text, fuzzy=True)
            if t.get("precision", True):
                r["precision"] = metrics.precision(t["tokens"], text)
        if "facts" in t:
            r["facts"] = metrics.facts(t["facts"], text, fuzzy=True)
        rows.append(r)

    def mean(k):
        vals = [r[k] for r in rows if r[k] is not None]
        return sum(vals) / len(vals) if vals else float("nan")

    return {k: round(mean(k), 3) for k in ("recall", "fuzzy", "facts", "precision")}


def objective(s: dict) -> float:
    """Single number to tune on: fuzzy word recall and fact recall, nudged by precision."""
    return round(0.4 * s["fuzzy"] + 0.4 * s["facts"] + 0.1 * s["recall"] + 0.1 * s["precision"], 4)


def cmd_run(a) -> None:
    prep_kw, eng_kw = json.loads(a.prep_kw), json.loads(a.eng_kw)
    t0 = time.time()
    lines = read_all(a.engine, a.prep, prep_kw, eng_kw)
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    (out / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), "utf-8")
    meta = {"engine": a.engine, "prep": a.prep, "prep_kw": prep_kw, "eng_kw": eng_kw}
    meta["seconds"] = round(time.time() - t0, 1)
    meta["dev"], meta["test"] = score_lines(lines, "dev"), score_lines(lines, "test")
    (out / "meta.json").write_text(json.dumps(meta, indent=1), "utf-8")
    print(json.dumps(meta))


GRIDS = {
    "tesseract": {
        "prep": [("raw", {}), ("gray", {"scale": 2.0}), ("ink", {"scale": 2.0, "close": 3})],
        "eng": {"psm": [4, 6, 11, 12], "lang": ["deu+eng", "eng"]},
    },
    "rapidocr": {
        "prep": [("raw", {}), ("ink", {"scale": 2.0, "close": 3}), ("ink", {"scale": 1.5, "close": 3})],
        "eng": {
            "text_score": [0.3, 0.5],
            "det_box_thresh": [0.3, 0.5],
            "det_unclip_ratio": [1.6, 2.2],
            "det_limit": [736, 1280],
        },
    },
    "easyocr": {
        "prep": [("raw", {}), ("ink", {"scale": 1.5, "close": 3}), ("ink", {"scale": 2.0, "close": 3})],
        "eng": {
            "text_threshold": [0.5, 0.7],
            "low_text": [0.3, 0.4],
            "decoder": ["greedy", "beamsearch"],
            "contrast_ths": [0.1, 0.3],
        },
    },
}


def ink_variants() -> list[tuple[str, dict]]:
    return [
        ("ink", {"scale": s, "close": c, "sat_min": sat})
        for s, c, sat in itertools.product([1.5, 2.0], [0, 3], [35, 55])
    ]


def cmd_tune(a) -> None:
    """Grid search on the dev pages only. Prints the table sorted best first."""
    grid = GRIDS[a.engine]
    keys = list(grid["eng"])
    results = []
    dev_pages = [n for n, t in TRUTH.items() if not n.startswith("_") and t["split"] == "dev"]
    for prep, prep_kw in grid["prep"]:
        for combo in itertools.product(*grid["eng"].values()):
            eng_kw = dict(zip(keys, combo, strict=True))
            lines = read_all(a.engine, prep, prep_kw, eng_kw, pages=dev_pages)
            s = score_lines(lines, "dev")
            results.append((objective(s), prep, prep_kw, eng_kw, s))
            print(results[-1], flush=True)
    results.sort(key=lambda r: -r[0])
    print("BEST", json.dumps(results[0], ensure_ascii=False))


def main() -> None:
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--engine", required=True, choices=sorted(ENGINES))
    r.add_argument("--prep", default="raw", choices=["raw", "gray", "ink"])
    r.add_argument("--prep-kw", default="{}")
    r.add_argument("--eng-kw", default="{}")
    r.add_argument("--out", required=True)
    r.set_defaults(func=cmd_run)
    t = sub.add_parser("tune")
    t.add_argument("--engine", required=True, choices=sorted(GRIDS))
    t.set_defaults(func=cmd_tune)
    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()

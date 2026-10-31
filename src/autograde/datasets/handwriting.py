"""Working subsets of the two handwriting datasets, split by student into tune and validate.

Only the working students are downloaded. Everyone else stays on the remote server as the sealed
benchmark: their ids are written to `split.json` for the record, but their files are never fetched,
so nothing can be tuned on them by accident. Run: `python -m autograde.datasets.handwriting`.

- Mendeley Data Science exam (CC BY 4.0): 50 students, scanned sheets, teacher marks per question.
- EDU-CIRCUIT-HW: the pages that carry a manually checked TA label, for a few students.

The split is a hash of the student id, so it never changes when more students are added.
"""

from __future__ import annotations

import csv
import hashlib
import http.client
import io
import json
import logging
import re
import subprocess
import time
import urllib.error
import urllib.request
import zipfile
from collections.abc import Callable
from pathlib import Path

from autograde.datasets.download import CIRCUIT_ROOT, CIRCUIT_ZIP, _RemoteFile

log = logging.getLogger(__name__)

MENDELEY_ZIP = "https://data.mendeley.com/public-api/zip/sf3kvjwknt/download/1"
MENDELEY_DIR = "A Dataset of Digitized Student Examination Papers,/"
MENDELEY_STUDENTS = 20  # of 50: 10 to tune on, 10 to validate on, 30 sealed
CIRCUIT_STUDENTS = 8  # of the 18 with TA labels: 4 to tune on, 4 to validate on, 10 sealed


class _RangedFile(_RemoteFile):
    """A `_RemoteFile` for a signed link.

    The size comes from a one-byte range read (HEAD is rejected) and an expired link (they last
    five minutes) is renewed with `renew()`.
    """

    def __init__(self, renew: Callable[[], str]) -> None:
        self.renew, self.pos = renew, 0
        self.url = renew()
        req = urllib.request.Request(self.url, headers={"Range": "bytes=0-0"})
        self.size = int(urllib.request.urlopen(req).headers["Content-Range"].split("/")[1])  # noqa: S310

    def readinto(self, buf) -> int:
        for attempt in range(5):
            try:
                return super().readinto(buf)
            except urllib.error.HTTPError as err:
                if err.code not in (403, 429) and err.code < 500 or attempt == 4:
                    raise
                if err.code == 403:  # a signed link has expired
                    self.url = self.renew()
                else:
                    time.sleep(3 * (attempt + 1))
            except (http.client.IncompleteRead, urllib.error.URLError, TimeoutError):
                if attempt == 4:
                    raise
                time.sleep(2 * (attempt + 1))
        return 0


def order(ids: list[str]) -> list[str]:
    """Ids in a fixed pseudo-random order that does not depend on which other ids exist."""
    return sorted(ids, key=lambda i: hashlib.sha1(i.encode()).hexdigest())


def split(ids: list[str], n: int) -> dict[str, list[str]]:
    """The first n ids in hash order are the working set, half tune and half validate."""
    ranked = order(ids)
    work, sealed = ranked[:n], ranked[n:]
    half = n // 2
    return {
        "tune": sorted(work[:half]),
        "validate": sorted(work[half:]),
        "benchmark": sorted(sealed),
    }


def _signed_url(url: str) -> str:
    head = subprocess.run(  # noqa: S603 - fixed https URL
        ["curl", "-sI", "-m", "30", "-A", "Mozilla/5.0", url],  # noqa: S607
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    found = re.search(r"(?im)^location:\s*(\S+)", head)
    if not found:
        raise RuntimeError("Mendeley gave no download link")
    return found.group(1)


def download_mendeley(data_dir: Path) -> dict:
    """Fetch the tune and validate sheets of the Mendeley exam and return the student split."""
    target = data_dir / "mendeley_exam"
    marks = target / "Teacher_manual_marks_Anonymized.csv"
    with marks.open(encoding="utf-8-sig") as f:
        students = [r["Student_ID"] for r in csv.DictReader(f)]
    parts = split(students, MENDELEY_STUDENTS)
    zf = zipfile.ZipFile(io.BufferedReader(_RangedFile(lambda: _signed_url(MENDELEY_ZIP)), 1 << 20))
    (target / "sheets").mkdir(parents=True, exist_ok=True)
    for sid in parts["tune"] + parts["validate"]:
        out = target / "sheets" / f"{sid}.pdf"
        if not out.exists():
            out.write_bytes(zf.read(f"{MENDELEY_DIR}Student_Pdf/{sid}.pdf"))
    (target / "split.json").write_text(json.dumps(parts, indent=1), encoding="utf-8")
    log.info("mendeley_exam: %d sheets", MENDELEY_STUDENTS)
    return parts


def download_circuit_pages(data_dir: Path) -> dict:
    """Fetch the labelled tune and validate pages of EDU-CIRCUIT-HW and return the student split."""
    target = data_dir / "circuit_hw"
    labels = target / "manually_checked_TA_label" / "valset1.csv"
    with labels.open(encoding="utf-8-sig", errors="replace") as f:
        rows = list(csv.DictReader(f))
    parts = split(sorted({r["Student ID"] for r in rows}), CIRCUIT_STUDENTS)
    work = set(parts["tune"] + parts["validate"])
    zf = zipfile.ZipFile(io.BufferedReader(_RangedFile(lambda: CIRCUIT_ZIP), 1 << 20))
    names = set(zf.namelist())
    got, missing = 0, []
    for r in rows:
        if r["Student ID"] not in work:
            continue
        rel = f"{r['Homework ID']}/{r['Student ID']}/{r['Question ID'].replace('_', '.')}.png"
        out = target / rel
        if out.exists():
            got += 1
        elif CIRCUIT_ROOT + rel in names:
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(zf.read(CIRCUIT_ROOT + rel))
            got += 1
        else:
            missing.append(rel)
    (target / "split.json").write_text(json.dumps(parts, indent=1), encoding="utf-8")
    log.info("circuit_hw: %d labelled pages, %d not in the archive", got, len(missing))
    return {**parts, "pages": got, "missing": missing}


INDIC_URL = "https://cvit.iiit.ac.in/images/datasets/indic_handwritten/{language}.zip"
INDIC_LANGUAGES = ("Hindi", "Bengali", "Tamil")  # three scripts: Devanagari, Bengali, Tamil
INDIC_PAGES = 12  # per language: 6 to tune on, 6 to validate on; the rest is the benchmark


def download_indic_words(data_dir: Path, languages: tuple[str, ...] = INDIC_LANGUAGES) -> dict:
    """Word images of a few handwritten pages per language (IIIT-Indic-HW-UC), with their text.

    The archive keeps, for each page, a text file listing `<page>_<k>.jpg<TAB>word` for every word
    and one cropped image per word. The words of a page are put back in reading order later
    (tools/ocr/compose_indic_pages.py). Pages are chosen by a hash of the page id; every other page
    is the sealed benchmark and is never fetched.
    """
    target = data_dir / "indic_words"
    manifest: dict[str, dict] = {}
    for language in languages:
        url = INDIC_URL.format(language=language)
        zf = zipfile.ZipFile(io.BufferedReader(_RangedFile(lambda u=url: u), 1 << 20))
        texts = [n for n in zf.namelist() if "/text/" in n and n.endswith(".txt")]
        by_key = {"/".join(n.split("/")[-3:]).removesuffix(".txt"): n for n in texts}
        parts = split(list(by_key), INDIC_PAGES)
        words: dict[str, list[dict]] = {}
        for page in parts["tune"] + parts["validate"]:
            txt_path = by_key[page]
            image_dir = txt_path.rsplit("/text/", 1)[0] + "/image/"
            rows = []
            for line in zf.read(txt_path).decode("utf-8").splitlines():
                file, _, text = line.partition("\t")
                out = target / language / "words" / file
                if not out.exists():
                    out.parent.mkdir(parents=True, exist_ok=True)
                    out.write_bytes(zf.read(image_dir + file))
                rows.append({"file": file, "text": text})
            words[page] = rows
        manifest[language] = {
            "tune": parts["tune"],
            "validate": parts["validate"],
            "benchmark_pages": len(parts["benchmark"]),
            "words": words,
        }
        log.info("indic_words %s: %d pages", language, INDIC_PAGES)
    target.mkdir(parents=True, exist_ok=True)
    (target / "split.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )
    return manifest


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    root = Path("data/raw")
    m = download_mendeley(root)
    c = download_circuit_pages(root)
    i = download_indic_words(root)
    print("mendeley tune", m["tune"], "validate", m["validate"])
    print("circuit tune", c["tune"], "validate", c["validate"], "pages", c["pages"])
    print("missing pages:", len(c["missing"]))
    print("indic:", {k: (len(v["tune"]), len(v["validate"])) for k, v in i.items()})

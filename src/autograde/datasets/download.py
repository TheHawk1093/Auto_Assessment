"""Fetch the stage-1 datasets into data/raw. Safe to run again: existing data is skipped."""

from __future__ import annotations

import csv
import io
import logging
import subprocess
import urllib.request
import zipfile
from pathlib import Path

log = logging.getLogger(__name__)

GIT_REPOS = {
    "digiklausur": "https://github.com/DigiKlausur/ASAG-Dataset.git",  # MPL-2.0
    "saf": "https://github.com/SebOchs/SAF.git",  # MIT; data also CC BY 4.0 on Hugging Face
}
# CC BY 4.0 mirror of Mohler et al. (2011)
MOHLER_URL = (
    "https://huggingface.co/datasets/Viswa45/ASAG/resolve/main/data/cleaned-oe-00001.parquet"
)


def download_all(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    for name, url in GIT_REPOS.items():
        target = data_dir / name
        if target.exists():
            log.info("%s already present, skipping", name)
            continue
        log.info("Cloning %s", name)
        subprocess.run(["git", "clone", "--depth", "1", url, str(target)], check=True)
    mohler = data_dir / "mohler" / "cleaned-oe-00001.parquet"
    if mohler.exists():
        log.info("mohler already present, skipping")
        return
    mohler.parent.mkdir(parents=True, exist_ok=True)
    log.info("Downloading mohler")
    urllib.request.urlretrieve(MOHLER_URL, mohler)  # noqa: S310 - fixed https URL


ENGSAF_BASE = "https://huggingface.co/datasets/IsmaelMousa/engsaf/resolve/main/"  # community copy


def download_engsaf(data_dir: Path) -> None:
    """EngSAF (benchmark only). Fetched on its own: `autograde download --engsaf`."""
    for name in ("train.csv", "validation.csv", "test.csv", "README.md"):
        target = data_dir / "engsaf" / name
        if target.exists():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        log.info("Downloading engsaf/%s", name)
        urllib.request.urlretrieve(ENGSAF_BASE + name, target)  # noqa: S310 - fixed https URL


HF = "https://huggingface.co/datasets/"
IELTS_FILE = "ielts_essay_evaluation_human_feedback.csv"
SEB_TEST = "test-00000-of-00001-9d9f92d314c93339.parquet"
# One small sample per task category, for the per-category prompts: name -> (file, url, max bytes)
SAMPLES = {
    "processbench": [  # maths, step-labelled solutions (Apache-2.0)
        ("gsm8k.json", HF + "Qwen/ProcessBench/resolve/main/gsm8k.json", None),
        ("math.json", HF + "Qwen/ProcessBench/resolve/main/math.json", None),
        ("olympiadbench.json", HF + "Qwen/ProcessBench/resolve/main/olympiadbench.json", None),
        ("omnimath.json", HF + "Qwen/ProcessBench/resolve/main/omnimath.json", None),
    ],
    "scibench": [  # college physics, chemistry and maths problems with worked solutions
        (f, HF + f"xw27/scibench/resolve/main/{f}", None)
        for f in ("fund.json", "fund_sol.json", "atkins.json", "atkins_sol.json")
    ],
    "scientsbank": [  # school science, 1 to 2 sentence answers, 5-way labels (CC)
        (
            "test.parquet",
            HF + "Spal09/sem_eval_2013_task_7/resolve/main/data/" + SEB_TEST,
            None,
        )
    ],
    "mathdial": [  # student maths errors with the teacher's note on the confusion
        (
            "test.jsonl",
            "https://raw.githubusercontent.com/eth-nlped/mathdial/main/data/test.jsonl",
            None,
        )
    ],
    "aes2": [  # persuasive essays, holistic score 1 to 6 (CC BY-NC); first 2 MB only
        ("train.csv", HF + "tasksource/AES2-essay-scoring/resolve/main/train.csv", 2_000_000)
    ],
    "asap_sas": [  # ASAP short answers, 10 prompts, score 0 to 3; the prompt holds the rubric
        ("train.csv", HF + "nlpatunt/D_ASAP-SAS/resolve/main/train.csv", 3_000_000)
    ],
    "imo_grading": [  # olympiad proofs graded 0 to 7 by humans, with grading guidelines (CC BY)
        (
            "train.parquet",
            HF + "Hwilner/imo-gradingbench/resolve/main/data/train-00000-of-00001.parquet",
            None,
        )
    ],
    "ielts": [  # IELTS essays with examiner feedback; first 1.5 MB only
        (
            "essays.csv",
            HF + "chillies/IELTS_essay_human_feedback/resolve/main/" + IELTS_FILE,
            1_500_000,
        )
    ],
}


def _fetch(url: str, target: Path, limit: int | None) -> None:
    """Download `url`; with a limit keep only the first rows (a cut CSV loses its last row)."""
    req = urllib.request.Request(url, headers={"Range": f"bytes=0-{limit - 1}"} if limit else {})
    with urllib.request.urlopen(req) as resp:  # noqa: S310 - fixed https URLs
        data = resp.read(limit) if limit else resp.read()
    if limit and len(data) >= limit:
        rows = list(csv.reader(io.StringIO(data.decode("utf-8", errors="ignore"))))[:-1]
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerows(rows)
        data = buf.getvalue().encode("utf-8")
    target.write_bytes(data)


def download_samples(data_dir: Path) -> None:
    """Small samples of datasets for other task types. `autograde download --samples`."""
    for name, files in SAMPLES.items():
        for fname, url, limit in files:
            target = data_dir / name / fname
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            log.info("Downloading %s/%s", name, fname)
            _fetch(url, target, limit)


CIRCUIT_ZIP = (
    "https://repository.gatech.edu/bitstreams/09496897-10b3-4675-bcf5-73b5b9802cd2/download"
)
CIRCUIT_ROOT = "EDU-CIRCUIT-HW_v1/Screenshot_output_anon/"


class _RemoteFile(io.RawIOBase):
    """A seekable view of a remote file, read with HTTP range requests."""

    def __init__(self, url: str) -> None:
        self.url, self.pos = url, 0
        head = urllib.request.Request(url, method="HEAD")
        self.size = int(urllib.request.urlopen(head).headers["Content-Length"])  # noqa: S310

    def seekable(self) -> bool:
        return True

    def readable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = 0) -> int:
        base = (0, self.pos, self.size)[whence]
        self.pos = base + offset
        return self.pos

    def readinto(self, buf) -> int:
        end = min(self.pos + len(buf), self.size) - 1
        if end < self.pos:
            return 0
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{end}"})
        data = urllib.request.urlopen(req).read()  # noqa: S310 - fixed https URL
        buf[: len(data)] = data
        self.pos += len(data)
        return len(data)


def download_circuit(data_dir: Path, images: int = 12) -> None:
    """EDU-CIRCUIT-HW without the 9 GB zip: the rubrics, the TA labels and a few handwritten
    pages from homework 1, read straight out of the remote archive. `download --circuit`."""
    target = data_dir / "circuit_hw"
    if (target / "rubric_outputs").exists():
        return
    zf = zipfile.ZipFile(io.BufferedReader(_RemoteFile(CIRCUIT_ZIP), 1 << 20))
    names = [n for n in zf.namelist() if n.startswith(CIRCUIT_ROOT) and not n.endswith("/")]
    wanted = [n for n in names if "/rubric_outputs/" in n or "/manually_checked_TA_label/" in n]
    pages = [n for n in names if "/Homework1/" in n and n.endswith(".png")]
    for name in wanted + pages[:images]:
        out = target / name.removeprefix(CIRCUIT_ROOT)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(zf.read(name))
    log.info("circuit_hw: %d files", len(wanted) + min(images, len(pages)))

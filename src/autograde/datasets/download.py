"""Fetch the stage-1 datasets into data/raw. Safe to run again: existing data is skipped."""

from __future__ import annotations

import csv
import io
import logging
import subprocess
import urllib.request
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

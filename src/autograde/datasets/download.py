"""Fetch the stage-1 datasets into data/raw. Safe to run again: existing data is skipped."""

from __future__ import annotations

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

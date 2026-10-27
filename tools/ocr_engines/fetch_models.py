"""Download the weights of every engine once, so later runs work offline.

.venv-ocr/Scripts/python tools/ocr_engines/fetch_models.py
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import ocr_engines as e  # noqa: E402


def main() -> None:
    from huggingface_hub import snapshot_download

    for name, load in [
        ("rapidocr (bundled)", e._rapid),
        ("easyocr", e._easyocr),
        ("doctr", e._doctr),
    ]:
        print("fetching", name, flush=True)
        load()
    for repo in (e.TROCR, e.GOT):
        print("fetching", repo, flush=True)
        snapshot_download(repo)
    print("done")


if __name__ == "__main__":
    main()

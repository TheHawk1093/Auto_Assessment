"""Runs one marking command detached from the UI and records how it ended.

Usage: python -m app.services.jobwrap <exam_dir> <kind> -- <command...>
The UI only reads job.json and job.log. job.json carries this process's id so a run that died
can be told from one still going, and so it can be cancelled.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _save(path: Path, state: dict) -> None:
    """Replace the file in one step, so the app never reads it half written."""
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state), encoding="utf-8")
    os.replace(tmp, path)


def main() -> None:
    """Run the command after `--`, logging its output and recording how it ended in job.json."""
    exam_dir, kind = Path(sys.argv[1]), sys.argv[2]
    cmd = sys.argv[sys.argv.index("--") + 1 :]
    job = exam_dir / "job.json"
    written = json.loads(job.read_text(encoding="utf-8")) if job.exists() else {}  # e.g. the model
    state = {
        **written,
        "kind": kind,
        "state": "running",
        "pid": os.getpid(),
        "started": datetime.now().isoformat(timespec="seconds"),
    }
    _save(job, state)
    with open(exam_dir / "job.log", "w", encoding="utf-8") as log:
        env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}  # Indic text in logs
        code = subprocess.run(
            cmd, stdout=log, stderr=subprocess.STDOUT, env=env, check=False
        ).returncode
    if json.loads(job.read_text(encoding="utf-8")).get("state") == "cancelled":
        return  # the UI already recorded the cancel
    state.update(
        state="done" if code == 0 else "failed",
        code=code,
        finished=datetime.now().isoformat(timespec="seconds"),
    )
    _save(job, state)
    _tell_owner(exam_dir, kind, code == 0)


WHAT = {"schemes": "Preparing", "mark": "Marking", "scan": "Reading the scanned sheets",
        "recheck": "The recheck"}  # fmt: skip


def _tell_owner(exam_dir: Path, kind: str, ok: bool) -> None:
    """Leave the exam's teacher a message that the job is over. Never lets a failure here matter."""
    try:
        from app.services import notifications

        meta = json.loads((exam_dir / "exam.json").read_text(encoding="utf-8"))
        text = f"{WHAT.get(kind, kind)} for {meta['title']} " + ("finished." if ok else "failed.")
        notifications.notify(meta.get("owner"), "job", text, meta["id"])
    except Exception:  # noqa: BLE001 - the job itself has already been recorded
        pass


if __name__ == "__main__":
    main()

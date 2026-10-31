"""Paths and constants for the web app. Change a location or limit here, nowhere else."""

from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP_DATA = Path(os.environ.get("AUTOGRADE_APP_DATA", ROOT / "app_data"))
DB = APP_DATA / "app.db"  # users, overrides, regrade requests, audit log
EXAMS = APP_DATA / "exams"  # one folder per exam: uploads, settings, job state
RUNS = ROOT / "runs"  # where `autograde exam` writes (same place as the CLI)
AUTOGRADE_CONFIG = "configs/exam.yaml"  # passed to the CLI as --config

DOC_EXT = {".txt", ".md", ".docx", ".pdf", ".json"}  # what the intake can read
MAX_ZIP_BYTES = 300 * 1024 * 1024  # unpacked size limit for an uploaded zip
STALE_START_S = 120  # a job that never reported a process id after this long is dead

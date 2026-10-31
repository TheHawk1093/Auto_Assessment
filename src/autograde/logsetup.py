"""Logging for the command line: the console as before, plus a rotating file in the logs folder."""

from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

FORMAT = "%(asctime)s %(levelname)s %(name)s %(message)s"
FILE_NAME = "autograde.log"
MAX_BYTES = 2_000_000  # per file; four older files are kept
_MARK = "_autograde_file"  # attribute that tells our handler from any other


def setup_logging(logs_dir: Path, command: str = "", level: int = logging.INFO) -> Path | None:
    """Send log records to the console and to `<logs_dir>/autograde.log`.

    Calling it again replaces the file handler rather than adding a second one. The file is
    skipped when the folder cannot be written, or when AUTOGRADE_NO_FILE_LOG is set (tests).

    Args:
        logs_dir: Folder for the log file; created if missing.
        command: Name of the command being run, written as the first line of the session.
        level: Lowest level recorded.

    Returns:
        The log file path, or None when only the console is used.

    """
    root = logging.getLogger()
    for h in [h for h in root.handlers if getattr(h, _MARK, False)]:
        root.removeHandler(h)
        h.close()
    if not any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        console = logging.StreamHandler()
        console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        root.addHandler(console)
    root.setLevel(level)
    if os.environ.get("AUTOGRADE_NO_FILE_LOG"):
        return None
    path = Path(logs_dir) / FILE_NAME
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        handler = RotatingFileHandler(path, maxBytes=MAX_BYTES, backupCount=4, encoding="utf-8")
    except OSError:
        return None  # a read-only checkout still works, with console logging only
    handler.setFormatter(logging.Formatter(FORMAT))
    setattr(handler, _MARK, True)
    root.addHandler(handler)
    logging.getLogger("autograde").info("session start: %s", command or " ".join(sys.argv[1:]))
    return path

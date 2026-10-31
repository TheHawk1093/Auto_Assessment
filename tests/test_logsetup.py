"""The command line writes a rotating log file in the logs folder."""

import logging

from autograde.logsetup import FILE_NAME, setup_logging


def _drop_file_handlers():
    root = logging.getLogger()
    for h in [h for h in root.handlers if getattr(h, "_autograde_file", False)]:
        root.removeHandler(h)
        h.close()


def test_records_reach_the_log_file(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTOGRADE_NO_FILE_LOG", raising=False)
    try:
        path = setup_logging(tmp_path / "logs", "exam")
        logging.getLogger("autograde.test").info("marked 3 answers")
        assert path == tmp_path / "logs" / FILE_NAME
        text = path.read_text(encoding="utf-8")
        assert "session start: exam" in text and "marked 3 answers" in text
    finally:
        _drop_file_handlers()


def test_setting_up_twice_keeps_one_file_handler(tmp_path, monkeypatch):
    monkeypatch.delenv("AUTOGRADE_NO_FILE_LOG", raising=False)
    try:
        setup_logging(tmp_path / "logs", "a")
        setup_logging(tmp_path / "logs", "b")
        ours = [h for h in logging.getLogger().handlers if getattr(h, "_autograde_file", False)]
        assert len(ours) == 1
    finally:
        _drop_file_handlers()


def test_no_file_when_switched_off(tmp_path, monkeypatch):
    monkeypatch.setenv("AUTOGRADE_NO_FILE_LOG", "1")
    assert setup_logging(tmp_path / "logs", "exam") is None
    assert not (tmp_path / "logs").exists()

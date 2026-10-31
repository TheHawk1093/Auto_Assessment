import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))  # lets tests import `fakes`


@pytest.fixture
def env(tmp_path, monkeypatch):
    """The web app pointed at a temporary folder: exams, runs and the database."""
    from app.services import db, storage

    monkeypatch.setattr(storage, "EXAMS", tmp_path / "exams")
    monkeypatch.setattr(storage, "RUNS", tmp_path / "runs")
    monkeypatch.setattr(db, "PATH", tmp_path / "app.db")
    return tmp_path

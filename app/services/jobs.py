"""Starts, watches and cancels `autograde exam` runs.

A run is a detached process (`jobwrap`) that writes job.json and job.log in the exam folder, so
the UI never holds the process: a browser refresh or a Streamlit restart loses nothing, and a run
whose process has died is reported as failed instead of running forever. One run at a time:
Goedel allows only four concurrent requests in total, so two marking runs must not overlap.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime

from app import config
from app.services import db, models, scans, settings_spec, storage
from app.services.storage import exam_dir, run_name, uploaded_files

ACTIVE = ("running",)


def build_command(exam_id: str, schemes_only: bool) -> list[str]:
    """The `autograde exam` command for an exam's files and settings."""
    meta = storage.load_meta(exam_id)
    settings = meta["settings"]
    config_path = models.write_config(models.get(meta["model"]), exam_dir(exam_id) / "config.yaml")
    paper = uploaded_files(exam_id, "paper")
    refs = uploaded_files(exam_id, "reference")
    answers = [p for p in uploaded_files(exam_id, "answers") if p.suffix.lower() != ".csv"]
    json_only = len(answers) == 1 and answers[0].suffix.lower() == ".json"
    answers_arg = answers[0] if json_only else storage.upload_dir(exam_id, "answers")

    cmd = [
        sys.executable, "-c", "from autograde.cli import main; main()",
        "--config", str(config_path), "exam",
        "--paper", str(paper[0]),
        "--answers", str(answers_arg),
        "--name", run_name(exam_id),
    ]  # fmt: skip
    if refs:
        cmd += ["--reference", *map(str, refs)]
    # The pipeline reads the student directory to tell who wrote each sheet: the database, then
    # the roster uploaded with the sheets (students it does not know yet).
    directory = [str(db.PATH)] if db.PATH.exists() else []
    directory += [str(p) for p in uploaded_files(exam_id, "answers") if p.suffix.lower() == ".csv"]
    if directory:
        cmd += ["--directory", *directory]
        if meta["course_id"] is not None and db.PATH.exists():
            cmd += ["--course-id", str(meta["course_id"])]
    fixes = exam_dir(exam_id) / "identity_fixes.json"
    if fixes.exists():
        cmd += ["--identity-fixes", str(fixes)]
    cmd += settings_spec.cli_args(settings)
    if schemes_only:
        cmd.append("--schemes-only")
    return cmd


# ---------- state ----------


def pid_alive(pid: int) -> bool:
    """Say whether a process with this id is still running."""
    if sys.platform == "win32":
        import ctypes

        kernel = ctypes.windll.kernel32
        handle = kernel.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        if not handle:
            return False
        code = ctypes.c_ulong()
        ok = kernel.GetExitCodeProcess(handle, ctypes.byref(code))
        kernel.CloseHandle(handle)
        return bool(ok) and code.value == 259  # STILL_ACTIVE
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    return True


def _write(exam_id: str, state: dict) -> None:
    (exam_dir(exam_id) / "job.json").write_text(json.dumps(state), encoding="utf-8")


def job_state(exam_id: str) -> dict:
    """Return the exam's job state.

    Returns:
        {} if there is no job, else kind, state (running, done, failed, cancelled) and times. A
        job marked running whose process is gone is turned into a failed one.
    """
    path = exam_dir(exam_id) / "job.json"
    if not path.exists():
        return {}
    state = json.loads(path.read_text(encoding="utf-8"))
    if state.get("state") == "running":
        pid = state.get("pid")
        age = (datetime.now() - datetime.fromisoformat(state["started"])).total_seconds()
        if (pid and not pid_alive(pid)) or (not pid and age > config.STALE_START_S):
            state.update(state="failed", note="The process stopped before it finished.")
            _write(exam_id, state)
    return state


def running_exam() -> str | None:
    """The id of the exam whose job is running, if any."""
    for meta in storage.list_exams():
        if job_state(meta["id"]).get("state") in ACTIVE:
            return meta["id"]
    return None


# ---------- control ----------


def _launch(exam_id: str, kind: str, cmd: list[str], model: str, **extra) -> None:
    """Record the job as running and start it detached."""
    _write(
        exam_id,
        {
            "kind": kind,
            "model": model,
            "state": "running",
            "started": datetime.now().isoformat(timespec="seconds"),
            **extra,
        },
    )
    flags = 0x00000008 | 0x00000200 if sys.platform == "win32" else 0  # detached, own group
    subprocess.Popen(
        [sys.executable, "-m", "app.services.jobwrap", str(exam_dir(exam_id)), kind, "--", *cmd],
        cwd=config.ROOT,
        creationflags=flags,
        start_new_session=sys.platform != "win32",
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def _check_free(exam_id: str) -> None:
    busy = running_exam()
    if busy:
        raise RuntimeError(f"Another job is running (exam {busy}). Wait for it to finish.")


def start(exam_id: str, schemes_only: bool) -> None:
    """Start a detached marking job for the exam.

    Args:
        exam_id: The exam to run.
        schemes_only: Write the marking schemes only, without marking.

    Raises:
        RuntimeError: If another job is running, files are missing or the model is unavailable.
    """
    _check_free(exam_id)
    answers = [p for p in uploaded_files(exam_id, "answers") if p.suffix.lower() != ".csv"]
    if not uploaded_files(exam_id, "paper") or not (answers or scans.sheets(exam_id)):
        raise RuntimeError("Upload the question paper and the student answers first.")
    unread = scans.unread(exam_id)
    if unread:
        raise RuntimeError(
            f"{len(unread)} scanned sheet(s) have not been read yet. Read them first "
            f"({', '.join(unread[:5])})."
        )
    option = models.get(storage.load_meta(exam_id)["model"])
    ok, why = models.availability(option)
    if not ok:
        raise RuntimeError(
            f"{option.label} cannot be used: {why} Choose another model in Settings."
        )
    kind = "schemes" if schemes_only else "mark"
    _launch(exam_id, kind, build_command(exam_id, schemes_only), option.id)


def build_scan_command(exam_id: str) -> list[str]:
    """The `autograde scan` command: read every scanned sheet that has no text document yet."""
    meta = storage.load_meta(exam_id)
    reader = models.get_reader(meta["reader"])
    config_path = models.write_config(models.get(meta["model"]), exam_dir(exam_id) / "config.yaml")
    cmd = [
        sys.executable, "-c", "from autograde.cli import main; main()",
        "--config", str(config_path), "scan", str(scans.folder(exam_id)),
        "--out", str(storage.upload_dir(exam_id, "answers")),
        "--summary", str(scans.summary_file(exam_id)),
        "--provider", reader.provider, "--model", reader.model,
    ]  # fmt: skip
    paper = uploaded_files(exam_id, "paper")
    if paper:
        cmd += ["--paper", str(paper[0])]
    known = scans.identities_file(exam_id)
    if known:
        cmd += ["--identities", str(known)]
    return cmd


def start_scan(exam_id: str) -> None:
    """Start a detached job that reads the exam's scanned sheets into text documents.

    Raises:
        RuntimeError: If another job is running, there is nothing to read or the reader is
            unavailable.
    """
    _check_free(exam_id)
    if not scans.unread(exam_id):
        raise RuntimeError("There are no unread scanned sheets.")
    reader = models.get_reader(storage.load_meta(exam_id)["reader"])
    ok, why = models.reader_availability(reader)
    if not ok:
        raise RuntimeError(f"{reader.label} cannot be used: {why} Choose another reader.")
    storage.upload_dir(exam_id, "answers").mkdir(parents=True, exist_ok=True)
    _launch(exam_id, "scan", build_scan_command(exam_id), reader.id)


def recheck_path(exam_id: str, request_id: int):
    """Where the proposal for a regrade request is written."""
    return exam_dir(exam_id) / "rechecks" / f"{request_id}.json"


def build_recheck_command(exam_id: str, model_id: str, student: str, question: str, note: str,
                          request_id: int) -> list[str]:  # fmt: skip
    """The `autograde recheck` command for one answer, marked by the chosen model option."""
    option = models.get(model_id)
    cfg = models.write_config(option, exam_dir(exam_id) / "config.recheck.yaml")
    out = recheck_path(exam_id, request_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    return [
        sys.executable, "-c", "from autograde.cli import main; main()",
        "--config", str(cfg), "recheck", "--name", run_name(exam_id),
        "--student", student, "--question", question, "--note", note, "--out", str(out),
    ]  # fmt: skip


def start_recheck(exam_id: str, request_id: int, model_id: str, student: str, question: str,
                  note: str) -> None:  # fmt: skip
    """Start a detached job that marks one answer again with the teacher's note.

    Raises:
        RuntimeError: If another job is running or the model is unavailable.
    """
    _check_free(exam_id)
    option = models.get(model_id)
    ok, why = models.availability(option)
    if not ok:
        raise RuntimeError(f"{option.label} cannot be used: {why}")
    recheck_path(exam_id, request_id).unlink(missing_ok=True)
    cmd = build_recheck_command(exam_id, model_id, student, question, note, request_id)
    _launch(exam_id, "recheck", cmd, option.id, request_id=request_id)


def cancel(exam_id: str) -> None:
    """Stop the run and everything it started."""
    state = job_state(exam_id)
    pid = state.get("pid")
    if state.get("state") == "running" and pid:
        if sys.platform == "win32":
            subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], capture_output=True)
        else:
            import signal

            os.killpg(pid, signal.SIGTERM)
    state.update(state="cancelled", finished=datetime.now().isoformat(timespec="seconds"))
    _write(exam_id, state)


def log_tail(exam_id: str, lines: int = 25) -> str:
    """Return the last `lines` lines of the job's log."""
    path = exam_dir(exam_id) / "job.log"
    if not path.exists():
        return ""
    return "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:])

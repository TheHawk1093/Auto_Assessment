"""Where student code is run: a container with nothing to harm.

Student code is untrusted, so it never runs in our own process. `wasm` (the default) runs it in
a WebAssembly CPython: nothing to install but `wasmtime` and one interpreter file, no admin rights
and no container engine, but only the standard library. `docker` starts a
throwaway container per job with no network, 256 MB of memory, a process cap, a read-only disk,
no capabilities and a non-root user; the container is removed when the job ends or times out.
`process` runs a child interpreter on the host: for trusted code on a machine you do not mind
risking, and only when asked for by name. If the container cannot be started the job is not run
(a failed start is reported, never turned into a host run).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import uuid
from functools import lru_cache
from pathlib import Path

IMAGE = "python:3.11-slim"
WASM = Path(__file__).resolve().parents[3] / "tools" / "sandbox" / "python.wasm"
WASM_LIB = WASM.parent / "lib"  # the standard library for that interpreter, if it needs one
WASM_MEMORY = 256 * 2**20
TIMEOUT_S = 10  # a container also has to start; the code's own limit is inside the runner

# Reads {"code": str, "tests": [str]} on stdin, runs each test line against the code, prints one
# JSON result. Its own prints are discarded so a student's output cannot forge the result.
RUNNER = r"""
import io, json, sys
try:
    import resource
    resource.setrlimit(resource.RLIMIT_AS, (512 * 2**20, 512 * 2**20))
except Exception:
    pass
job = json.loads(sys.stdin.read())
real_out = sys.stdout
sys.stdout = io.StringIO()  # not os.devnull: WASI has none
scope = {"__name__": "student"}
result = {"loaded": True, "error": "", "passed": 0, "failed": []}
try:
    exec(compile(job["code"], "student.py", "exec"), scope)
except BaseException as exc:
    result["loaded"], result["error"] = False, type(exc).__name__ + ": " + str(exc)[:200]
if result["loaded"]:
    for test in job["tests"]:
        try:
            exec(compile(test, "test", "exec"), scope)
            result["passed"] += 1
        except BaseException as exc:
            why = type(exc).__name__ + ": " + str(exc)[:80]
            result["failed"].append(test[:120] + "  -> " + why)
real_out.write(json.dumps(result))
"""


class SandboxError(RuntimeError):
    """The job could not be run at all (no container engine, image missing, timeout)."""


@lru_cache(maxsize=1)
def docker_ready() -> str:
    """An empty string when containers work, else the reason they do not."""
    try:
        info = subprocess.run(
            ["docker", "info", "--format", "{{.ServerVersion}}"],  # noqa: S607
            capture_output=True, text=True, timeout=20,
        )  # fmt: skip
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"docker is not available ({type(exc).__name__})"
    if info.returncode != 0:
        return "the docker engine is not running"
    have = subprocess.run(
        ["docker", "image", "inspect", IMAGE],  # noqa: S607
        capture_output=True, timeout=20,
    )  # fmt: skip
    if have.returncode != 0:
        pull = subprocess.run(
            ["docker", "pull", "-q", IMAGE],  # noqa: S607
            capture_output=True, text=True, timeout=300,
        )  # fmt: skip
        if pull.returncode != 0:
            return f"the image {IMAGE} is missing and could not be pulled"
    return ""


def _run_wasm(payload: str) -> str:
    """Run the job inside a WebAssembly CPython.

    It has no network, no files except a read-only copy of the standard library, a memory cap,
    and a deadline that stops an endless loop.
    """
    import threading

    from wasmtime import Config, Engine, Linker, Module, Store, WasiConfig

    if not WASM.exists():
        raise SandboxError(f"{WASM} is missing; see DESIGN.md (code sandbox)")
    config = Config()
    config.epoch_interruption = True
    engine = Engine(config)
    with tempfile.TemporaryDirectory() as tmp:
        files = {n: Path(tmp) / n for n in ("in", "out", "err")}
        files["in"].write_text(payload, encoding="utf-8")
        wasi = WasiConfig()
        wasi.argv = ["python", "-I", "-c", RUNNER]
        wasi.stdin_file, wasi.stdout_file, wasi.stderr_file = (str(files[n]) for n in files)
        if WASM_LIB.exists():
            wasi.preopen_dir(str(WASM_LIB), "/usr/local/lib/python3.11")
        store = Store(engine)
        store.set_limits(memory_size=WASM_MEMORY)
        store.set_wasi(wasi)
        store.set_epoch_deadline(1)
        timer = threading.Timer(TIMEOUT_S, engine.increment_epoch)
        timer.start()
        try:
            linker = Linker(engine)
            linker.define_wasi()
            instance = linker.instantiate(store, Module.from_file(engine, str(WASM)))
            instance.exports(store)["_start"](store)
        except Exception as exc:  # exit(0) also arrives here; the output file tells which
            if "interrupt" in str(exc).lower() or "epoch" in str(exc).lower():
                raise SandboxError(f"timed out after {TIMEOUT_S} s") from exc
        finally:
            timer.cancel()
        out = files["out"].read_text(encoding="utf-8")
        if not out.strip():
            raise SandboxError(f"no result from the code ({files['err'].read_text()[-120:]})")
        return out


def run_job(job: dict, mode: str = "wasm") -> dict:
    """Run {"code", "tests"} and return the runner's result.

    Raises:
        SandboxError: When the job could not be run (as opposed to the student's code
            failing, which is a normal result).
    """
    payload = json.dumps(job)
    if mode == "docker":
        if reason := docker_ready():
            raise SandboxError(reason)
        name = f"autograde-{uuid.uuid4().hex[:12]}"
        cmd = [
            "docker", "run", "--rm", "-i", "--name", name,
            "--network", "none", "--memory", "256m", "--memory-swap", "256m", "--cpus", "1",
            "--pids-limit", "64", "--read-only", "--tmpfs", "/tmp:size=16m",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges", "--user", "65534:65534",
            IMAGE, "python", "-I", "-c", RUNNER,
        ]  # fmt: skip
        try:
            proc = subprocess.run(  # noqa: S603
                cmd, input=payload, capture_output=True, text=True, timeout=TIMEOUT_S
            )
        except subprocess.TimeoutExpired as exc:
            subprocess.run(["docker", "rm", "-f", name], capture_output=True)  # noqa: S607
            raise SandboxError(f"timed out after {TIMEOUT_S} s") from exc
    elif mode == "wasm":
        try:
            return json.loads(_run_wasm(payload))
        except json.JSONDecodeError as exc:
            raise SandboxError("the code printed no readable result") from exc
    elif mode == "process":
        with tempfile.TemporaryDirectory() as tmp:
            try:
                proc = subprocess.run(  # noqa: S603
                    [sys.executable, "-I", "-c", RUNNER], input=payload, capture_output=True,
                    text=True, timeout=TIMEOUT_S, cwd=tmp,
                    env={"PATH": os.environ.get("PATH", "")},
                )  # fmt: skip
            except subprocess.TimeoutExpired as exc:
                raise SandboxError(f"timed out after {TIMEOUT_S} s") from exc
    else:
        raise ValueError(f"unknown sandbox {mode!r}: use wasm, docker or process")
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise SandboxError(f"no result from the code ({proc.stderr.strip()[-120:]})") from exc

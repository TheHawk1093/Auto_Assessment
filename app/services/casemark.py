"""Mark the seeded demo cases with the real pipeline and save each marked run.

    python -m app.services.casemark all          # or case1 case2 case3 case4

This calls OpenRouter, so it spends credit (DeepSeek V4.1 Flash is the cheap default; a case costs
a few cents to a few tens of cents). The marked runs are saved by `cases.snapshot`, and
`python -m app.services.cases seed` puts them back, so this is needed once per set of cases.
Handwritten sheets (case 2) are read first with the exam's reader.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import yaml

from app import config
from app.services import cases, jobs, storage

WORKERS = 4  # parallel marking calls inside one case


def _launch(case: str, command: list[str], log: Path) -> subprocess.Popen:
    cfg_path = Path(command[command.index("--config") + 1])
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    cfg["pipeline"]["max_workers"] = WORKERS
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return subprocess.Popen(
        command, cwd=config.ROOT, stdout=log.open("w", encoding="utf-8"), stderr=subprocess.STDOUT
    )


def mark(selected: list[str]) -> dict[str, bool]:
    """Read (case 2), mark and save the cases in parallel. Returns {case: succeeded}."""
    logs = config.APP_DATA / "casemark_logs"
    logs.mkdir(parents=True, exist_ok=True)
    running: dict[str, subprocess.Popen] = {}
    for case in selected:
        eid = cases.EXAM_ID[case]
        if not (cases.available(case) == "" and storage.exam_dir(eid).exists()):
            print(f"{case}: not seeded here, skipped")
            continue
        if case == "case2":
            scan = jobs.build_scan_command(eid)
            done = subprocess.run(
                scan, cwd=config.ROOT, stdout=(logs / "case2_scan.log").open("w"),
                stderr=subprocess.STDOUT, check=False,
            )  # fmt: skip
            if done.returncode:
                print("case2: reading the handwriting failed, see", logs / "case2_scan.log")
                continue
        running[case] = _launch(
            case, jobs.build_command(eid, schemes_only=False), logs / f"{case}.log"
        )
        print(f"{case}: marking, log {logs / (case + '.log')}", flush=True)
    result = {}
    while running:
        for case, proc in list(running.items()):
            if proc.poll() is not None:
                running.pop(case)
                ok = (
                    proc.returncode == 0
                    and (storage.run_path(cases.EXAM_ID[case]) / "marks.csv").exists()
                )
                if ok:
                    cases.snapshot(case)
                result[case] = ok
                print(f"{case}: {'marked and saved' if ok else 'FAILED, see its log'}", flush=True)
        time.sleep(5)
    return result


def main() -> None:
    """Command line: `casemark all` or `casemark case1 case3 ...`."""
    args = sys.argv[1:]
    chosen = list(cases.CASE_DIR) if args == ["all"] else args
    if not chosen or any(c not in cases.CASE_DIR for c in chosen):
        sys.exit("usage: python -m app.services.casemark all | case1 case2 case3 case4")
    outcome = mark(chosen)
    sys.exit(0 if outcome and all(outcome.values()) else 1)


if __name__ == "__main__":
    main()

"""Experiment log of runs, with settings, prompt fingerprint and score against the teacher.

Each run adds one line with its settings, prompt fingerprint and score against the
teacher's marks, plus a readable table. Purpose: know what changed, what it did, and what to
fall back to.

Files (committed to git, unlike output/runs/):
    experiments/log.jsonl    machine-readable, append-only
    experiments/RESULTS.md   table rebuilt from the log, with change against earlier runs
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

from autograde import prompts

LOG_PATH = Path("experiments/log.jsonl")
RESULTS_PATH = Path("experiments/RESULTS.md")


def prompt_fingerprint() -> dict[str, str]:
    """Short hash of every prompt file, plus one hash for the whole set."""
    parts = {
        name: hashlib.sha1(path.read_bytes()).hexdigest()[:8]
        for name, path in sorted(prompts.files().items())
    }
    total = hashlib.sha1("".join(f"{k}{v}" for k, v in parts.items()).encode()).hexdigest()[:8]
    return {"all": total, **parts}


def sample_key(entry: dict) -> str:
    """Two entries are comparable when they graded the same sample."""
    return f"{entry['dataset']}/{entry['split']}/n{entry['n']}/seed{entry['seed']}"


def append_entry(entry: dict, log_path: Path = LOG_PATH) -> None:
    """Append one entry to the log file as a JSON line."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_log(log_path: Path = LOG_PATH) -> list[dict]:
    """Return all entries in the log file, or an empty list if there is none."""
    if not log_path.exists():
        return []
    lines = log_path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def make_entry(run_dir: Path, variant: str, note: str = "") -> dict:
    """Build a log entry from a finished run folder (run.json, metrics.json, usage.json)."""
    setup = json.loads((run_dir / "run.json").read_text(encoding="utf-8"))
    metrics = json.loads((run_dir / "metrics.json").read_text(encoding="utf-8"))
    usage_path = run_dir / "usage.json"
    usage = json.loads(usage_path.read_text(encoding="utf-8")) if usage_path.exists() else {}
    return {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "variant": variant,
        "note": note,
        "run": run_dir.name,
        "dataset": setup["dataset"],
        "split": setup["split"],
        "n": setup["n"],
        "seed": setup["seed"],
        "mode": setup["mode"],
        "model": f"{setup['llm']['backend']}-{setup['llm']['model']}",
        "pipeline": setup.get("pipeline", {}),
        "prompts": prompt_fingerprint(),
        "overall": metrics["overall"],
        "by_band": {k: {"n": v.get("n", 0), "mean_abs_error": v.get("mean_abs_error")}
                    for k, v in metrics.get("by_band", {}).items()},
        "flagged_share": metrics.get("flagged_share"),
        "cost_usd": usage.get("cost_usd"),
        "calls": usage.get("calls"),
    }  # fmt: skip


def _f(v: float | None, digits: int = 3) -> str:
    return "-" if v is None else f"{v:.{digits}f}"


def _delta(new: float | None, old: float | None, lower_is_better: bool) -> str:
    if new is None or old is None:
        return "-"
    d = new - old
    if abs(d) < 0.0005:
        return "="
    better = (d < 0) == lower_is_better
    return f"{'▲' if better else '▼'} {d:+.3f}"


def comparisons(entries: list[dict], i: int) -> tuple[str, str]:
    """Change in error for entry i against the baseline and the previous run on the same sample."""
    e, key = entries[i], sample_key(entries[i])
    err = e["overall"].get("mean_abs_error")
    earlier = entries[:i]
    base = next((b for b in reversed(earlier)
                 if b["mode"] == "baseline" and sample_key(b) == key), None)  # fmt: skip
    prev = next((p for p in reversed(earlier)
                 if p["mode"] == e["mode"] and sample_key(p) == key), None)  # fmt: skip
    if e["mode"] == "baseline" or base is None:
        vs_base = "-"
    else:
        vs_base = _delta(err, base["overall"].get("mean_abs_error"), True)
    vs_prev = "-" if prev is None else _delta(err, prev["overall"].get("mean_abs_error"), True)
    return vs_base, vs_prev


def render_markdown(entries: list[dict]) -> str:
    """Render all runs as a markdown table.

    'vs base' compares with the baseline on the same sample; 'vs prev' with the previous run
    of the same mode on the same sample. ▲ better, ▼ worse.
    """
    lines = [
        "# Experiment results",
        "",
        "Generated from `experiments/log.jsonl`. Do not edit.",
        "Scores are against the teacher's marks.",
        "Error = average gap as a share of total marks (lower is better). "
        "Bias below 0 means stricter than the teacher.",
        "▲ better, ▼ worse. Compare only rows on the same sample.",
        "",
        "| Time | Variant | Run | Sample | Mode | Error | vs base | vs prev | Bias | Correl. | QWK "
        "| Flagged | Cost $ | Prompts |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, e in enumerate(entries):
        o = e["overall"]
        key = sample_key(e)
        err = o.get("mean_abs_error")
        vs_base, vs_prev = comparisons(entries, i)
        flagged = e.get("flagged_share")
        lines.append(
            f"| {e['ts'][:16].replace('T', ' ')} | {e['variant']} | {e['run']} | {key} "
            f"| {e['mode']} | {_f(err)} | {vs_base} | {vs_prev} | {_f(o.get('bias'))} "
            f"| {_f(o.get('pearson'), 2)} | {_f(o.get('qwk'), 2)} "
            f"| {'-' if flagged is None else f'{flagged:.0%}'} | {_f(e.get('cost_usd'), 2)} "
            f"| {e['prompts']['all']} |"
        )
    lines += ["", "## Variants", ""]
    seen: dict[str, dict] = {}
    for e in entries:
        seen.setdefault(e["variant"], e)
    for name, e in seen.items():
        note = (e["note"] or "no note").rstrip(".")
        lines.append(f"- **{name}**: {note}. Settings: `{json.dumps(e['pipeline'])}`")
    return "\n".join(lines) + "\n"


def record_run(run_dir: Path, variant: str, note: str = "") -> Path:
    """Append the run to the log and rebuild RESULTS.md. Returns the table path."""
    entry = make_entry(run_dir, variant, note)
    if entry["overall"].get("n"):  # a run that marked nothing (quota, outage) is not a result
        append_entry(entry)
    RESULTS_PATH.write_text(render_markdown(read_log()), encoding="utf-8")
    return RESULTS_PATH

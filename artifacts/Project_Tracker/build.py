"""Rebuild tracker.html from tracker.json and the metrics of two runs.

Usage:  python artifacts/Project_Tracker/build.py
Edit tracker.json only. The numbers in the results table are read from
runs/<name>/metrics.json and usage.json, so they are never typed by hand.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent


def _run(name: str) -> tuple[dict, dict]:
    run = ROOT / "runs" / name
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))["overall"]
    usage = json.loads((run / "usage.json").read_text(encoding="utf-8"))
    return metrics, usage


def metric_rows(baseline: str, pipeline: str) -> list[dict]:
    (mb, ub), (mp, up) = _run(baseline), _run(pipeline)
    return [
        {"name": "Average error (share of total marks)", "better": "lower", "max": 0.5,
         "baseline": mb["mean_abs_error"], "pipeline": mp["mean_abs_error"]},
        {"name": "Correlation with teacher marks", "better": "higher", "max": 1.0,
         "baseline": mb["pearson"], "pipeline": mp["pearson"]},
        {"name": "Agreement score (QWK)", "better": "higher", "max": 1.0,
         "baseline": mb["qwk"], "pipeline": mp["qwk"]},
        {"name": "Bias (negative is strict)", "better": "closer to 0", "max": 0.3, "bias": True,
         "baseline": mb["bias"], "pipeline": mp["bias"]},
        {"name": "Cost, US dollars at list price", "better": "lower", "max": 1.0,
         "baseline": ub["cost_usd"], "pipeline": up["cost_usd"]},
    ]  # fmt: skip


def main() -> None:
    data = json.loads((HERE / "tracker.json").read_text(encoding="utf-8"))
    cmp = data.pop("compare", None)
    if cmp:
        data["results_title"] = cmp["title"]
        data["results_note"] = cmp["note"]
        data["metrics"] = metric_rows(cmp["baseline"], cmp["pipeline"])
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\/")
    html = (HERE / "template.html").read_text(encoding="utf-8").replace("__DATA__", blob)
    (HERE / "tracker.html").write_text(html, encoding="utf-8")
    print("wrote", HERE / "tracker.html")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as exc:
        sys.exit(f"Missing file: {exc.filename}")

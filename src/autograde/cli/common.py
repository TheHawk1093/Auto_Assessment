"""Helpers shared by the command modules."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from autograde.config import LLMConfig, PipelineConfig, Settings
from autograde.evaluation.experiments import (
    comparisons,
    prompt_fingerprint,
    read_log,
    record_run,
)
from autograde.evaluation.metrics import report
from autograde.llm import build_client, client_name
from autograde.pipeline.rubric import RubricStore
from autograde.pipeline.run import read_results, to_question
from autograde.schemas import Result
from autograde.vcs import GitError, commit_experiment
from autograde.viewer import sample_by_mark, sample_spread, write_report


def run_dir(settings: Settings, name: str) -> Path:
    return settings.paths.runs_dir / name


def load_run(settings: Settings, name: str) -> list[Result]:
    return read_results(run_dir(settings, name) / "results.jsonl")


def load_run_with_feedback(
    settings: Settings, name: str, sample: int | None = None
) -> list[Result]:
    """The finished run's results that have feedback, optionally N of them spread over the marks."""
    results = [r for r in load_run(settings, name) if r.feedback]
    if not results:
        sys.exit("No results with feedback in that run.")
    return sample_by_mark(results, sample) if sample else results


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_setup(run: Path) -> dict:
    path = run / "run.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def run_client_name(setup: dict, settings: Settings) -> str:
    """The model name a run was made with, which also keys its stored marking schemes."""
    return client_name(LLMConfig.model_validate(setup.get("llm") or settings.llm.model_dump()))


def run_pipeline(run: Path, settings: Settings) -> PipelineConfig:
    """The pipeline settings a run was made with (falls back to the current config)."""
    saved = read_setup(run).get("pipeline")
    return PipelineConfig.model_validate(saved) if saved else settings.pipeline


def records_for(results: list[Result], settings: Settings, cfg: PipelineConfig | None = None):
    """Stored marking schemes for the questions in `results` (same path as the run used)."""
    cfg = cfg or settings.pipeline
    store = RubricStore(
        settings.paths.rubrics_dir,
        build_client(settings.llm),
        cfg.rubric_selftest,
        cfg.rubric_variant,
    )
    return {r.item.question_key: store.get(to_question(r.item)) for r in results}


def write_view(
    run: Path, settings: Settings, limit: int | None = None, seed: int = 0, by: str = "question"
) -> Path:
    """Build report.html from a run folder: answers, marks, quotes, feedback, judgements."""
    setup = read_setup(run)
    model = run_client_name(setup, settings)
    judged = {}
    jpath = run / "feedback_judgements.jsonl"
    if jpath.exists():
        for line in jpath.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            judged[row.pop("id")] = row
    results = read_results(run / "results.jsonl")
    if limit:
        results = (
            sample_by_mark(results, limit) if by == "mark" else sample_spread(results, limit, seed)
        )
    info = {}
    if setup:
        info = {
            "variant": setup.get("variant"),
            "mode": setup.get("mode"),
            "model": model,
            "prompts": prompt_fingerprint()["all"],
            "settings": setup.get("pipeline", {}) if setup.get("mode") == "pipeline" else {},
        }
    return write_report(
        results,
        run / ("report_sample.html" if limit else "report.html"),
        run.name + (f" (sample of {len(results)})" if limit else ""),
        settings.paths.rubrics_dir,
        model,
        judged,
        info,
    )


def finish(
    run: Path, results: list[Result], usage: dict, settings: Settings, args: argparse.Namespace
) -> None:
    """Score against the teacher, write the report, log the run, commit and tag."""
    summary = report(results)
    write_json(run / "metrics.json", summary)
    write_json(run / "usage.json", usage)
    print(json.dumps(summary, indent=2))
    print("usage:", usage)
    print("report:", write_view(run, settings))
    print("logged:", record_run(run, args.variant or args.mode, args.note))
    if not args.no_commit:
        entries = read_log()
        vs_base, vs_prev = comparisons(entries, len(entries) - 1)
        try:
            print("committed and tagged:", commit_experiment(entries[-1], vs_base, vs_prev))
        except GitError as exc:
            print("git step skipped:", exc)


def save_derived_run(
    settings: Settings,
    args: argparse.Namespace,
    results: list[Result],
    setup: dict,
    changes: dict,
    usage: dict,
) -> None:
    """Write a run that reuses another run's answers with one setting changed, then finish it."""
    dst = run_dir(settings, args.new_name)
    dst.mkdir(parents=True, exist_ok=True)
    setup = {**setup, "variant": args.variant, "pipeline": {**setup["pipeline"], **changes}}
    write_json(dst / "run.json", setup)
    write_lines(dst / "results.jsonl", [r.model_dump_json() for r in results])
    finish(dst, results, usage, settings, args)

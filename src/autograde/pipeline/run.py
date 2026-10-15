"""Run the pipeline (or the baseline) over a list of items, in parallel, with resume."""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Literal

from autograde.config import PipelineConfig, Settings
from autograde.llm import LLMClient
from autograde.pipeline.baseline import grade_baseline
from autograde.pipeline.feedback import write_feedback
from autograde.pipeline.grade import mark_answer
from autograde.pipeline.read import read_answer
from autograde.pipeline.rubric import RubricStore
from autograde.schemas import Item, Question, Result, RubricRecord

log = logging.getLogger(__name__)
Mode = Literal["pipeline", "baseline"]


def to_question(item: Item) -> Question:
    return Question(
        key=item.question_key,
        text=item.question,
        model_answer=item.model_answer,
        max_mark=item.max_mark,
    )


def grade_item(item: Item, record: RubricRecord, client: LLMClient, cfg: PipelineConfig) -> Result:
    """Stages 3 to 5 for one answer: read it, mark it, check the marking, write feedback."""
    rubric = record.rubric
    reading = read_answer(item, client) if cfg.read_first else None
    grading, flags = mark_answer(
        to_question(item),
        rubric,
        item.student_answer,
        client,
        retries=cfg.grade_retries,
        reading=reading,
        evidence_policy=cfg.evidence_policy,
        policy=cfg.policy,
        partial_weight=cfg.partial_weight if cfg.mark_rule == "status" else None,
    )
    if record.selftest_passed is False:
        flags = [*flags, "scheme_failed_selftest"]
    feedback = write_feedback(item, rubric, grading, client)
    return Result(
        item=item,
        mode="pipeline",
        predicted_mark=grading.total,
        reading=reading,
        grading=grading,
        feedback=feedback,
        flags=flags,
    )


def read_results(path: Path) -> list[Result]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [Result.model_validate_json(line) for line in f if line.strip()]


def run_items(
    items: list[Item],
    mode: Mode,
    client: LLMClient,
    settings: Settings,
    out_path: Path,
    progress: Callable[[int, int], None] | None = None,
) -> list[Result]:
    """Grade all items, appending each result to `out_path` as it finishes.

    Items already in `out_path` are skipped, so an interrupted run can be resumed.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = {r.item.id: r for r in read_results(out_path)}
    todo = [i for i in items if i.id not in done]
    workers = settings.pipeline.max_workers
    log.info("%d items, %d already done, %d to run", len(items), len(done), len(todo))

    records: dict[str, RubricRecord] = {}
    if mode == "pipeline" and todo:
        store = RubricStore(
            settings.paths.cache_dir,
            client,
            run_selftest=settings.pipeline.rubric_selftest,
            variant=settings.pipeline.rubric_variant,
        )
        questions = {i.question_key: to_question(i) for i in todo}
        with ThreadPoolExecutor(workers) as pool:
            futures = {pool.submit(store.get, q): k for k, q in questions.items()}
            for fut in as_completed(futures):
                records[futures[fut]] = fut.result()
        log.info("%d marking schemes ready", len(records))

    def work(item: Item) -> Result:
        if mode == "baseline":
            return grade_baseline(item, client)
        return grade_item(item, records[item.question_key], client, settings.pipeline)

    results = list(done.values())
    with ThreadPoolExecutor(workers) as pool, out_path.open("a", encoding="utf-8") as sink:
        futures = {pool.submit(work, i): i for i in todo}
        for n, fut in enumerate(as_completed(futures), 1):
            try:
                res = fut.result()
            except Exception:
                log.exception("Failed on %s", futures[fut].id)
                continue
            sink.write(res.model_dump_json() + "\n")
            sink.flush()
            results.append(res)
            if progress:
                progress(n, len(todo))
    return results

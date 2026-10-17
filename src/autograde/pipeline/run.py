"""Run the pipeline (or the baseline) over a list of items, in parallel, with resume."""

from __future__ import annotations

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Literal, NamedTuple

from autograde.config import PipelineConfig, Settings
from autograde.llm import LLMClient, build_client
from autograde.pipeline.baseline import grade_baseline
from autograde.pipeline.feedback import write_feedback
from autograde.pipeline.grade import mark_answer
from autograde.pipeline.read import read_answer
from autograde.pipeline.rubric import RubricStore
from autograde.pipeline.verify import apply_form_gate
from autograde.pipeline.vote import combine, models_disagree
from autograde.schemas import Grading, Item, Question, Reading, Result, RubricRecord

log = logging.getLogger(__name__)
Mode = Literal["pipeline", "baseline"]


def to_question(item: Item) -> Question:
    return Question(
        key=item.question_key,
        text=item.question,
        model_answer=item.model_answer,
        max_mark=item.max_mark,
    )


class Marked(NamedTuple):
    reading: Reading | None
    grading: Grading
    flags: list[str]
    votes: list[float]  # total of each marking when voting, else empty


def mark_item(item: Item, record: RubricRecord, client: LLMClient, cfg: PipelineConfig) -> Marked:
    """Stages 3 and 4 for one answer: read it, mark it (several times if voting), check it."""
    rubric = record.rubric
    weight = cfg.partial_weight if cfg.mark_rule == "status" else None
    if cfg.votes > 1 and weight is None:
        raise ValueError("votes > 1 needs mark_rule: status")
    reading = read_answer(item, client) if cfg.read_first else None

    def once(_: int) -> tuple[Grading, list[str]]:
        return mark_answer(
            to_question(item),
            rubric,
            item.student_answer,
            client,
            retries=cfg.grade_retries,
            reading=reading,
            evidence_policy=cfg.evidence_policy,
            policy=cfg.policy,
            partial_weight=weight,
        )

    if cfg.votes <= 1:
        grading, flags = once(0)
        votes: list[float] = []
    else:
        with ThreadPoolExecutor(cfg.votes) as pool:
            runs = list(pool.map(once, range(cfg.votes)))
        votes = [g.total for g, _ in runs]
        grading, split = combine([g for g, _ in runs], rubric, item.student_answer, weight)
        flags = sorted({f for _, fl in runs for f in fl}) + [f"vote_split:{p}" for p in split]
    grading, gate_flag = apply_form_gate(grading, reading, item.max_mark)
    if gate_flag:
        flags = [*flags, gate_flag]
    if record.selftest_passed is False:
        flags = [*flags, "scheme_failed_selftest"]
    return Marked(reading, grading, flags, votes)


def grade_item(
    item: Item,
    record: RubricRecord,
    client: LLMClient,
    cfg: PipelineConfig,
    second: tuple[LLMClient, dict[str, RubricRecord]] | None = None,
) -> Result:
    """Stages 3 to 5 for one answer: read it, mark it, check the marking, write feedback.

    With `second` (a cheaper model and its schemes) the answer is marked again, and a big gap
    between the two marks adds the flag `models_disagree`: the grader may be wrong here.
    """
    reading, grading, flags, votes = mark_item(item, record, client, cfg)
    second_mark = None
    if second is not None:
        other, records = second
        second_mark = mark_item(item, records[item.question_key], other, cfg).grading.total
        if models_disagree(grading.total, second_mark, item.max_mark, cfg.disagree_gap):
            flags = [*flags, "models_disagree"]
    feedback = write_feedback(
        item, record.rubric, grading, client, cfg.feedback_variant, cfg.feedback_n
    )
    return Result(
        item=item,
        mode="pipeline",
        predicted_mark=grading.total,
        reading=reading,
        grading=grading,
        feedback=feedback,
        votes=votes,
        second_mark=second_mark,
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
    questions = {i.question_key: to_question(i) for i in todo}
    if mode == "pipeline" and todo:
        store = RubricStore(
            settings.paths.cache_dir,
            client,
            run_selftest=settings.pipeline.rubric_selftest,
            variant=settings.pipeline.rubric_variant,
        )
        with ThreadPoolExecutor(workers) as pool:
            futures = {pool.submit(store.get, q): k for k, q in questions.items()}
            for fut in as_completed(futures):
                records[futures[fut]] = fut.result()
        log.info("%d marking schemes ready", len(records))

    second = None
    if mode == "pipeline" and todo and settings.pipeline.second_model:
        second_client = build_client(
            settings.llm.model_copy(
                update={"model": settings.pipeline.second_model, "effort": None}
            )
        )
        second_store = RubricStore(
            settings.paths.cache_dir,
            second_client,
            run_selftest=settings.pipeline.rubric_selftest,
            variant=settings.pipeline.rubric_variant,
        )
        with ThreadPoolExecutor(workers) as pool:
            second_records = dict(
                zip(questions, pool.map(second_store.get, questions.values()), strict=True)
            )
        second = (second_client, second_records)

    def work(item: Item) -> Result:
        if mode == "baseline":
            return grade_baseline(item, client)
        return grade_item(item, records[item.question_key], client, settings.pipeline, second)

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

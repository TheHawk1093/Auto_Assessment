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
from autograde.pipeline.cascade import unsure_because
from autograde.pipeline.checks import run_checks
from autograde.pipeline.codetests import generate_tests
from autograde.pipeline.feedback import write_feedback
from autograde.pipeline.figure import Describer, make_describer
from autograde.pipeline.grade import mark_answer
from autograde.pipeline.levels import LEVEL_PARTIAL_WEIGHT, LEVEL_POLICY
from autograde.pipeline.objective import mark_mcq
from autograde.pipeline.read import read_answer
from autograde.pipeline.rubric import RubricStore, store_for
from autograde.pipeline.verify import apply_form_gate, snap_grading
from autograde.pipeline.vote import combine, models_disagree
from autograde.schemas import (
    NOT_GIVEN,
    Grading,
    Item,
    Question,
    Reading,
    Result,
    RubricRecord,
)

log = logging.getLogger(__name__)
Mode = Literal["pipeline", "baseline"]
TEACHER_POLICY = {"lenient": "essence", "moderate": "balanced", "strict": "strict"}
TEACHER_WEIGHT = {"lenient": 0.9, "moderate": 0.7, "strict": 0.5}  # share for a partial verdict


def to_question(item: Item) -> Question:
    return Question(
        key=item.question_key,
        text=item.question,
        model_answer=item.model_answer.strip() or NOT_GIVEN,
        max_mark=item.max_mark,
        kind=item.kind,
        rubric=item.rubric,
        field=item.field,
    )


class Marked(NamedTuple):
    reading: Reading | None
    grading: Grading
    flags: list[str]
    votes: list[float]  # total of each marking when voting, else empty
    evidence: str = ""  # what code checks found (numbers, units, syntax, a drawing)


def mark_item(
    item: Item,
    record: RubricRecord,
    client: LLMClient,
    cfg: PipelineConfig,
    describe: Describer | None = None,
) -> Marked:
    """Stages 3 and 4 for one answer: read it, mark it (several times if voting), check it.

    Code checks for the kind of question (numbers and units, code, a drawing) run first and give
    the marker facts; some of them also decide the marks of the points they cover.
    """
    rubric = record.rubric
    if item.kind == "mcq":  # a choice is checked by code; no model marks it
        grading, flags = mark_mcq(item, rubric)
        return Marked(None, grading, flags, [])
    weight = cfg.partial_weight if cfg.mark_rule == "status" else None
    policy = cfg.policy
    if rubric.level:  # a rubric written at a level makes the grader follow that level
        policy = LEVEL_POLICY[rubric.level]
        weight = LEVEL_PARTIAL_WEIGHT[rubric.level]
    if cfg.teacher.strictness:  # the teacher's wish decides how tightly a point is judged
        policy = TEACHER_POLICY[cfg.teacher.strictness]
        if weight is not None and not rubric.level:
            weight = TEACHER_WEIGHT[cfg.teacher.strictness]
    step = cfg.teacher.mark_step
    policy = rubric.policy or policy  # a rubric can also set its own tightness
    if rubric.partial_weight is not None and weight is not None:
        weight = rubric.partial_weight
    if cfg.votes > 1 and weight is None:
        raise ValueError("votes > 1 needs mark_rule: status")
    reading = read_answer(item, client, cfg.ocr is not None) if cfg.read_first else None
    notes = cfg.teacher.for_question(item.question_key)
    checks = run_checks(item, rubric, cfg, describe)

    def once(_: int) -> tuple[Grading, list[str]]:
        return mark_answer(
            to_question(item),
            rubric,
            item.student_answer,
            client,
            retries=cfg.grade_retries,
            reading=reading,
            evidence_policy=cfg.evidence_policy,
            policy=policy,
            partial_weight=weight,
            deductions=cfg.deductions,
            granularity=cfg.teacher.partial_credit,
            mark_step=step,
            notes=notes,
            evidence=checks.evidence,
            earlier=item.earlier if cfg.teacher.follow_through else "",
        )

    if cfg.votes <= 1:
        grading, flags = once(0)
        votes: list[float] = []
    else:
        with ThreadPoolExecutor(cfg.votes) as pool:
            runs = list(pool.map(once, range(cfg.votes)))
        votes = [g.total for g, _ in runs]
        grading, split = combine(
            [g for g, _ in runs],
            rubric,
            item.student_answer,
            weight,
            cfg.teacher.partial_credit,
            step,
        )
        flags = sorted({f for _, fl in runs for f in fl}) + [f"vote_split:{p}" for p in split]
    grading, decided = checks.decide(grading, rubric)  # points settled by code replace the model
    flags = [*flags, *decided]
    grading, gate_flag = apply_form_gate(grading, reading, item.max_mark, item.question)
    if gate_flag:
        flags = [*flags, gate_flag]
    if step:
        grading = snap_grading(grading, rubric, step)
    flags = [*flags, *checks.flags]
    if record.selftest_passed is False:
        flags = [*flags, "scheme_failed_selftest"]
    return Marked(reading, grading, flags, votes, checks.evidence)


def grade_item(
    item: Item,
    record: RubricRecord,
    client: LLMClient,
    cfg: PipelineConfig,
    second: tuple[LLMClient, dict[str, RubricRecord]] | None = None,
    stronger: LLMClient | None = None,
    describe: Describer | None = None,
) -> Result:
    """Stages 3 to 5 for one answer: read it, mark it, check the marking, write feedback.

    With `second` (a cheaper model and its schemes) the answer is marked again, and a big gap
    between the two marks adds the flag `models_disagree`: the grader may be wrong here.
    """
    item = item.with_key(record.rubric.answer_key)  # a missing model answer is replaced by the key
    reading, grading, flags, votes, evidence = mark_item(item, record, client, cfg, describe)
    second_mark = None
    if second is not None:
        other, records = second
        second_mark = mark_item(
            item, records[item.question_key], other, cfg, describe
        ).grading.total
        if models_disagree(grading.total, second_mark, item.max_mark, cfg.disagree_gap):
            flags = [*flags, "models_disagree"]
    first_mark = None
    if stronger is not None:  # the cheap marking stands unless it looks unsure
        why = unsure_because(grading, flags, item.max_mark, cfg.escalate_when)
        if why:
            first_mark = grading.total
            reading, grading, flags, votes, evidence = mark_item(
                item, record, stronger, cfg, describe
            )
            flags = [*flags, "escalated:" + "+".join(why)]
    feedback = None
    if cfg.with_feedback:
        feedback = write_feedback(
            item,
            record.rubric,
            grading,
            client,
            cfg.feedback_variant,
            cfg.feedback_n,
            notes=cfg.teacher.for_question(item.question_key),
            language=cfg.feedback_language,
            evidence=evidence,
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
        first_mark=first_mark,
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
        store = store_for(settings, grader=client)
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
            settings.paths.rubrics_dir,
            second_client,
            run_selftest=settings.pipeline.rubric_selftest,
            variant=settings.pipeline.rubric_variant,
            teacher=settings.pipeline.teacher,
            review=settings.pipeline.rubric_review,
        )
        with ThreadPoolExecutor(workers) as pool:
            second_records = dict(
                zip(questions, pool.map(second_store.get, questions.values()), strict=True)
            )
        second = (second_client, second_records)

    stronger = None
    if mode == "pipeline" and todo and settings.pipeline.escalate_model:
        stronger = build_client(
            settings.llm.model_copy(
                update={
                    "model": settings.pipeline.escalate_model,
                    "effort": None,
                    "backend": settings.pipeline.strong_backend or settings.llm.backend,
                }
            )
        )

    describe = make_describer(settings) if any(i.figures for i in todo) else None
    pcfg = settings.pipeline
    if mode == "pipeline" and pcfg.code_exec:  # tests for code questions that came without any
        made: dict[str, str] = {}
        for i, item in enumerate(todo):
            if item.kind == "code" and not item.tests.strip():
                if item.question_key not in made:
                    made[item.question_key] = generate_tests(
                        item, client, pcfg.code_sandbox,
                        settings.paths.rubrics_dir / "code_tests", pcfg.code_tests_n,
                    )  # fmt: skip
                if made[item.question_key]:
                    todo[i] = item.model_copy(
                        update={"tests": made[item.question_key], "tests_generated": True}
                    )

    def work(item: Item) -> Result:
        if mode == "baseline":
            return grade_baseline(item, client)
        record = records[item.question_key]
        return grade_item(item, record, client, settings.pipeline, second, stronger, describe)

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
    if stronger is not None:
        client.usage.add(stronger.usage)  # the run's cost includes the re-marking
    return results

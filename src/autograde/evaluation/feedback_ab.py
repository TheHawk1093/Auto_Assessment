"""Feedback A/B: does feedback built from the marking beat feedback written from the answers alone?

Two approaches on the same marked answers:
- graded: the feedback writer is given the checked marking (the pipeline's normal stage 5).
- alone: the writer sees only question, model answer and student answer and finds the gaps itself.

Each approach is written by each of two model families. The simulated student who rewrites the
answer (revision) or answers a different question on the same idea (transfer) is always the OTHER
family, so a model is never improved by its own feedback. One fixed grader marks every rewrite.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from autograde.config import PipelineConfig
from autograde.evaluation.revision import RevisionRow, revision_test
from autograde.evaluation.revision import summarise as summarise_revision
from autograde.evaluation.transfer import summarise as summarise_transfer
from autograde.evaluation.transfer import transfer_test
from autograde.llm import LLMClient
from autograde.pipeline.feedback import write_feedback
from autograde.pipeline.feedback_alone import write_feedback_alone
from autograde.schemas import Feedback, Result, RubricRecord

APPROACHES = ("graded", "alone")


def lost_marks(results: Sequence[Result]) -> list[Result]:
    """The answers that can gain: graded, not blank, below full marks."""
    return [
        r
        for r in results
        if r.grading and r.item.student_answer.strip() and r.predicted_mark < r.item.max_mark
    ]


def _feedback(
    r: Result, approach: str, writer: LLMClient, records: Mapping[str, RubricRecord], variant: str
) -> Feedback:
    if approach == "alone":
        return write_feedback_alone(r.item, writer)
    assert r.grading is not None
    rubric = records[r.item.question_key].rubric
    return write_feedback(r.item, rubric, r.grading, writer, variant)


def feedback_for(
    results: Sequence[Result],
    approach: str,
    writer: LLMClient,
    records: Mapping[str, RubricRecord],
    variant: str,
    cache_path: Path,
    workers: int,
) -> list[Result]:
    """Results carrying the new feedback. Written once per (approach, writer, answer) and cached."""
    cache: dict[str, dict] = {}
    if cache_path.exists():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))

    def one(r: Result) -> Result:
        if r.item.id not in cache:
            cache[r.item.id] = _feedback(r, approach, writer, records, variant).model_dump()
        return r.model_copy(update={"feedback": Feedback.model_validate(cache[r.item.id])})

    with ThreadPoolExecutor(workers) as pool:
        out = list(pool.map(one, results))
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
    return out


def _rev_gain(rows: Sequence[RevisionRow]) -> dict[str, float]:
    """Per answer: mark gained from feedback beyond a rewrite without it, as a share of total."""
    return {r.id: (r.with_feedback - r.without_feedback) / r.max_mark for r in rows}


def _trn_gain(rows: Sequence) -> dict[str, float]:
    return {r.id: (r.with_feedback - r.without_feedback) / r.max_mark for r in rows}


def run_ab(
    results: Sequence[Result],
    records: Mapping[str, RubricRecord],
    grader: LLMClient,
    other: LLMClient,
    cfg: PipelineConfig,
    out_dir: Path,
    runs_dir: Path,
    workers: int = 4,
) -> dict:
    """Four cells: {graded, alone} x {writer = grader's family, writer = the other family}."""
    todo = lost_marks(results)
    out_dir.mkdir(parents=True, exist_ok=True)
    cells: dict[str, dict] = {}
    gains: dict[str, dict[str, dict[str, dict[str, float]]]] = {}
    for writer, student in ((other, grader), (grader, other)):
        for approach in APPROACHES:
            tag = f"{approach}|writer={writer.name}|student={student.name}"
            safe = tag.replace("|", "_").replace("/", "-").replace(":", "-")
            with_fb = feedback_for(
                todo,
                approach,
                writer,
                records,
                cfg.feedback_variant,
                out_dir / f"feedback_{safe}.json",
                workers,
            )
            rev = revision_test(
                with_fb, records, grader, student, cfg, out_dir / "control.json", workers
            )
            trn = transfer_test(with_fb, grader, student, grader, runs_dir, workers)
            words = [len(r.feedback.text().split()) for r in with_fb if r.feedback]
            cells[tag] = {
                "approach": approach,
                "writer": writer.name,
                "student": student.name,
                "revision": summarise_revision(rev),
                "transfer": summarise_transfer(trn),
                "mean_feedback_words": round(sum(words) / max(len(words), 1), 1),
            }
            gains.setdefault(writer.name, {})[approach] = {
                "rev": _rev_gain(rev),
                "trn": _trn_gain(trn),
            }
            (out_dir / f"rows_{safe}.json").write_text(
                json.dumps(
                    {
                        "revision": [x.model_dump() for x in rev],
                        "transfer": [x.model_dump() for x in trn],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
    return {"n_answers_tested": len(todo), "cells": cells, "paired": paired(gains)}


def paired(gains: Mapping[str, Mapping]) -> list[dict]:
    """graded minus alone, per writer, on the same answers (positive: the marking helps)."""
    out = []
    for writer, pair in gains.items():
        row: dict = {"writer": writer}
        for kind in ("rev", "trn"):
            g, a = pair["graded"][kind], pair["alone"][kind]
            ids = sorted(set(g) & set(a))
            row[f"n_{kind}"] = len(ids)
            row[f"{kind}_graded_minus_alone"] = round(
                sum(g[i] - a[i] for i in ids) / max(len(ids), 1), 4
            )
        out.append(row)
    return out


def table(report: Mapping) -> str:
    """A readable summary of the four cells and the paired differences."""
    lines = [
        "| approach | writer | student | n | rev gain (fb) | rev gain (none) | rev lift | leak | "
        "transfer lift | words |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for c in report["cells"].values():
        r, t = c["revision"], c["transfer"]
        lines.append(
            f"| {c['approach']} | {c['writer']} | {c['student']} | {r.get('n', 0)} | "
            f"{r.get('gain_with_feedback', '')} | {r.get('gain_without_feedback', '')} | "
            f"{r.get('lift', '')} | {r.get('leak_in_feedback', '')} | "
            f"{t.get('transfer_lift', '')} | {c['mean_feedback_words']} |"
        )
    lines.append("")
    for p in report["paired"]:
        lines.append(
            f"writer {p['writer']}: graded minus alone = revision {p['rev_graded_minus_alone']:+} "
            f"(n={p['n_rev']}), transfer {p['trn_graded_minus_alone']:+} (n={p['n_trn']})"
        )
    return "\n".join(lines)

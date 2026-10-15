"""Deterministic checks on a model's marking. No model calls here."""

from __future__ import annotations

import re

from autograde.schemas import EPS, Grading, PointVerdict, Rubric

_FRAGMENT_SPLIT = re.compile(r"\s*(?:\.\.\.|…|\s\|\s)\s*")
_MIN_FRAGMENT = 3


def _norm(text: str) -> str:
    """Lowercase, collapse whitespace, drop quote marks, so quotes match despite formatting."""
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", text.lower().replace('"', "")).strip()


def evidence_in_answer(evidence: str, answer: str) -> bool:
    """True if every quoted fragment appears in the answer. Fragments are split on '...'."""
    haystack = _norm(answer)
    fragments = [f for f in _FRAGMENT_SPLIT.split(_norm(evidence)) if len(f) >= _MIN_FRAGMENT]
    return bool(fragments) and all(f in haystack for f in fragments)


def check_grading(grading: Grading, rubric: Rubric, answer: str) -> list[str]:
    """Return a list of problems, empty if the marking is acceptable."""
    problems: list[str] = []
    points = {p.id: p for p in rubric.points}
    seen: set[str] = set()
    for v in grading.verdicts:
        p = points.get(v.point_id)
        if p is None:
            problems.append(f"{v.point_id}: not a point in the marking scheme.")
            continue
        if v.point_id in seen:
            problems.append(f"{v.point_id}: marked more than once.")
        seen.add(v.point_id)
        problems += _check_verdict(v, p.marks, answer)
    problems += [f"{pid}: no verdict given." for pid in points if pid not in seen]
    return problems


def _check_verdict(v: PointVerdict, worth: float, answer: str) -> list[str]:
    out: list[str] = []
    m = v.marks_awarded
    if m > worth + EPS:
        out.append(f"{v.point_id}: {m:g} marks awarded but the point is worth {worth:g}.")
    if v.status == "not_met" and m > EPS:
        out.append(f"{v.point_id}: status not_met but {m:g} marks awarded.")
    if v.status == "met" and abs(m - worth) > EPS:
        out.append(f"{v.point_id}: status met but marks are {m:g}, not the full {worth:g}.")
    if v.status == "partial" and not (EPS < m < worth - EPS):
        out.append(f"{v.point_id}: status partial needs marks strictly between 0 and {worth:g}.")
    if m > EPS and not evidence_in_answer(v.evidence, answer):
        out.append(f"{v.point_id}: evidence is empty or not copied exactly from the answer.")
    return out


def repair(grading: Grading, rubric: Rubric, answer: str) -> tuple[Grading, list[str]]:
    """Make a grading valid after retries failed, erring on the side of no credit.

    Missing points get 0, over-awards are capped, unsupported credit is removed.
    Every change is reported as a flag so it shows up in the results.
    """
    flags: list[str] = []
    by_id: dict[str, PointVerdict] = {}
    for v in grading.verdicts:
        by_id.setdefault(v.point_id, v)
    fixed: list[PointVerdict] = []
    for p in rubric.points:
        v = by_id.get(p.id)
        if v is None:
            flags.append(f"repaired:{p.id}:missing")
            fixed.append(PointVerdict(point_id=p.id, status="not_met", marks_awarded=0,
                                      reason="No verdict was produced."))  # fmt: skip
            continue
        marks = min(v.marks_awarded, p.marks)
        if marks > EPS and not evidence_in_answer(v.evidence, answer):
            flags.append(f"repaired:{p.id}:unsupported_evidence")
            fixed.append(v.model_copy(update={"status": "not_met", "marks_awarded": 0.0,
                                              "evidence": ""}))  # fmt: skip
            continue
        status = "not_met" if marks <= EPS else "met" if marks >= p.marks - EPS else "partial"
        if marks != v.marks_awarded or status != v.status:
            flags.append(f"repaired:{p.id}:marks_or_status")
        fixed.append(v.model_copy(update={"status": status, "marks_awarded": marks}))
    return Grading(verdicts=fixed), flags

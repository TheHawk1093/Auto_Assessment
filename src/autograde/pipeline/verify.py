"""Deterministic checks on a model's marking. No model calls here."""

from __future__ import annotations

import re

from autograde.schemas import EPS, Grading, PointVerdict, Rubric

_FRAGMENT_SPLIT = re.compile(r"\s*(?:\.\.\.|…|\s\|\s)\s*")
_MIN_FRAGMENT = 3
_MIN_SQUASHED = 4


def _norm(text: str) -> str:
    """Lowercase, collapse whitespace, drop quote marks, so quotes match despite formatting."""
    text = text.replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", text.lower().replace('"', "")).strip()


def _squash(text: str) -> str:
    """Letters and digits only. Lets a quote match even when spacing or symbols differ, as
    happens with formulas such as 'W(t+1) = W(t) + n*e*X' versus 'W(t+1)=W(t)+n e X'."""
    return re.sub(r"[\W_]+", "", text.lower())


def evidence_in_answer(evidence: str, answer: str) -> bool:
    """True if every quoted fragment appears in the answer. Fragments are split on '...'.

    First an exact match ignoring case and spacing; failing that, a match on letters and
    digits only (fragments need at least a few such characters, so it cannot match by chance).
    """
    haystack = _norm(answer)
    squashed = _squash(answer)
    fragments = [f for f in _FRAGMENT_SPLIT.split(_norm(evidence)) if len(f) >= _MIN_FRAGMENT]
    if not fragments:
        return False

    def found(frag: str) -> bool:
        if frag in haystack:
            return True
        sq = _squash(frag)
        return len(sq) >= _MIN_SQUASHED and sq in squashed

    return all(found(f) for f in fragments)


def check_grading(
    grading: Grading, rubric: Rubric, answer: str, require_evidence: bool = True
) -> list[str]:
    """Return a list of problems, empty if the marking is acceptable.

    With require_evidence False, quotes that cannot be found are not a problem here: use
    `unverified_points` to report them without throwing the marking away.
    """
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
        problems += _check_verdict(v, p.marks, answer, require_evidence)
    problems += [f"{pid}: no verdict given." for pid in points if pid not in seen]
    return problems


def _check_verdict(v: PointVerdict, worth: float, answer: str, require_evidence: bool) -> list[str]:
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
    if require_evidence and m > EPS and not evidence_in_answer(v.evidence, answer):
        out.append(f"{v.point_id}: evidence is empty or not copied exactly from the answer.")
    return out


def unverified_points(grading: Grading, answer: str) -> list[str]:
    """Ids of points that earned marks but whose quote cannot be found in the answer."""
    return [
        v.point_id
        for v in grading.verdicts
        if v.marks_awarded > EPS and not evidence_in_answer(v.evidence, answer)
    ]


def repair(
    grading: Grading, rubric: Rubric, answer: str, zero_unsupported: bool = True
) -> tuple[Grading, list[str]]:
    """Make a grading valid after retries failed.

    Missing points get 0 and over-awards are capped. If `zero_unsupported`, credit whose quote
    cannot be found is removed (the strict policy); otherwise it is kept and only reported.
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
            fixed.append(
                PointVerdict(
                    point_id=p.id,
                    status="not_met",
                    marks_awarded=0,
                    reason="No verdict was produced.",
                )
            )
            continue
        marks = min(v.marks_awarded, p.marks)
        if zero_unsupported and marks > EPS and not evidence_in_answer(v.evidence, answer):
            flags.append(f"repaired:{p.id}:unsupported_evidence")
            fixed.append(
                v.model_copy(update={"status": "not_met", "marks_awarded": 0.0, "evidence": ""})
            )
            continue
        status = "not_met" if marks <= EPS else "met" if marks >= p.marks - EPS else "partial"
        if marks != v.marks_awarded or status != v.status:
            flags.append(f"repaired:{p.id}:marks_or_status")
        fixed.append(v.model_copy(update={"status": status, "marks_awarded": marks}))
    return Grading(verdicts=fixed), flags

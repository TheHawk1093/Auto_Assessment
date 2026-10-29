"""Deterministic checks on a model's marking. No model calls here."""

from __future__ import annotations

import difflib
import math
import re
import unicodedata

from autograde.schemas import EPS, Deducted, Grading, PointVerdict, Reading, Rubric, RubricPoint
from autograde.textutil import words

_FRAGMENT_SPLIT = re.compile(r"\s*(?:\.\.\.|…|\s\|\s)\s*")
_MIN_FRAGMENT = 3
_MIN_SQUASHED = 8
_NEAR_MIN_CHARS = 24  # shorter quotes must match exactly
_NEAR_BLOCK = 4  # a matching run shorter than this is chance
_NEAR_SHARE = 0.85  # share of the quote that must be found in such runs
SHORT_ANSWER_WORDS = 25  # an unquoted credit on an answer this short cites the whole answer


def _unicode(text: str) -> str:
    """Canonical form for comparing text in any script: composed (NFC) and without the invisible
    joiners that OCR and keyboards add or drop inside Indic words."""
    return unicodedata.normalize("NFC", text).replace("‌", "").replace("‍", "")


def _norm(text: str) -> str:
    """Lowercase, collapse whitespace, drop quote marks, so quotes match despite formatting."""
    text = _unicode(text).replace("“", '"').replace("”", '"').replace("’", "'")
    return re.sub(r"\s+", " ", text.lower().replace('"', "")).strip()


def _squash(text: str) -> str:
    """Letters and digits only. Lets a quote match even when spacing or symbols differ, as
    happens with formulas such as 'W(t+1) = W(t) + n*e*X' versus 'W(t+1)=W(t)+n e X'.
    It ignores operators on purpose: the check asks whether the quote was copied from the
    answer at all, not whether every sign is identical. Combining marks (the vowel signs of
    Indic scripts) are kept, because they are part of the word."""
    return "".join(
        c for c in _unicode(text).lower() if c.isalnum() or unicodedata.category(c).startswith("M")
    )


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
        if len(sq) >= _MIN_SQUASHED and sq in squashed:
            return True
        return _near_copy(frag, haystack)

    return all(found(f) for f in fragments)


def _near_copy(frag: str, haystack: str) -> bool:
    """A quote that is the answer's own words with a few characters changed (a corrected typo, a
    dropped symbol). Needs most of the quote in long runs, close together: scattered letters or a
    reworded sentence do not count. Quoted answers like this are marked as well as exact ones."""
    if len(frag) < _NEAR_MIN_CHARS:
        return False
    blocks = [
        b
        for b in difflib.SequenceMatcher(None, haystack, frag, autojunk=False).get_matching_blocks()
        if b.size >= _NEAR_BLOCK
    ]
    if not blocks:
        return False
    covered = sum(b.size for b in blocks)
    spread = blocks[-1].a + blocks[-1].size - blocks[0].a
    return covered >= _NEAR_SHARE * len(frag) and spread <= 1.3 * len(frag) + 10


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
    elif m > EPS and not v.evidence.strip():  # a quote that is off is tolerated, a missing one not
        out.append(f"{v.point_id}: marks given but no words quoted from the answer as evidence.")
    return out


GRANULARITY_SHARES = {"none": (), "half": (0.5,), "quarter": (0.25, 0.5, 0.75)}


def allowed_shares(
    point: RubricPoint | None, partial_weight: float, granularity: str = "rubric"
) -> tuple[float, ...]:
    """The shares of a point's marks that a partial verdict may be worth.

    A point's own levels win (the rubric writer already followed the teacher's granularity);
    otherwise the teacher's granularity; otherwise the one default share.
    """
    if point is not None and point.levels:
        return tuple(sorted(lv.share for lv in point.levels))
    if granularity in GRANULARITY_SHARES:
        return GRANULARITY_SHARES[granularity]
    return (partial_weight,)


def snap(fraction: float, shares: tuple[float, ...]) -> float:
    """The allowed share nearest to what the model proposed (the lower one on a tie)."""
    if not shares:
        return 0.0
    return min(sorted(shares), key=lambda s: abs(s - fraction))


def to_step(marks: float, step: float, ceiling: float) -> float:
    """`marks` rounded to the nearest multiple of `step` (halves go up), never above `ceiling`."""
    return round(min(math.floor(marks / step + 0.5) * step, ceiling), 6)


def partial_in_steps(proposed: float, full: float, step: float) -> float | None:
    """A partial verdict worth a whole number of steps, strictly between 0 and `full`. None when
    the point is too small to have a step between nothing and everything."""
    low, high = step, full - step
    if high < low - EPS:
        return None
    return min(max(to_step(proposed, step, full), low), to_step(high, step, high))


def apply_mark_rule(
    grading: Grading,
    rubric: Rubric,
    partial_weight: float,
    granularity: str = "rubric",
    mark_step: float | None = None,
) -> Grading:
    """Turn each verdict into marks in code.

    met = full marks, not_met = 0, partial = one of the point's allowed shares of its marks
    (the one nearest to the model's own figure; with a single share that share). With
    `mark_step` a partial verdict is instead worth the model's own figure rounded to a multiple
    of the step, so a 2-mark point can earn 1.8 when the step is 0.2.

    The model decides the verdict (what the student achieved). Code decides what a verdict is
    worth, so one setting controls how generous the marking is and marks always agree with
    the verdicts that the feedback is written from. The model's own figure is kept in model_marks.
    """
    points = {p.id: p for p in rubric.points}
    out: list[PointVerdict] = []
    for v in grading.verdicts:
        point = points.get(v.point_id)
        full = point.marks if point else v.marks_awarded
        if v.status == "met":
            marks = full
        elif v.status == "partial":
            proposed = v.model_marks if v.model_marks is not None else v.marks_awarded
            stepped = partial_in_steps(proposed, full, mark_step) if mark_step else None
            marks = (
                stepped
                if stepped is not None
                else full
                * snap(
                    proposed / full if full else 0.0,
                    allowed_shares(point, partial_weight, granularity),
                )
            )
        else:
            marks = 0.0
        out.append(
            v.model_copy(
                update={
                    "marks_awarded": round(marks, 6),
                    "model_marks": v.model_marks if v.model_marks is not None else v.marks_awarded,
                }
            )
        )
    return grading.model_copy(update={"verdicts": out})


EXPLAIN_WORDS = re.compile(
    r"\b(explain|describe|justify|derive|why|how|reason|discuss|compare|differentiate|elaborate)",
    re.IGNORECASE,
)


def apply_form_gate(
    grading: Grading, reading: Reading | None, max_mark: float, question: str = ""
) -> tuple[Grading, str | None]:
    """Act on how the answer is written, which the generous marking rules cannot see.

    Scrambled text earns nothing. A bare list of terms, where an explanation was asked for,
    earns at most half the marks, but only when the question text really asks for an explanation
    (the reader model sometimes mistakes a requested list for a bare keyword list).
    Returns the grading and a flag when it was changed.
    """
    if reading is None:
        return grading, None
    if reading.form == "incoherent":
        zeroed = [
            v.model_copy(update={"status": "not_met", "marks_awarded": 0.0, "evidence": ""})
            for v in grading.verdicts
        ]
        return grading.model_copy(update={"verdicts": zeroed}), "incoherent_answer"
    asks_why = not question or EXPLAIN_WORDS.search(question)
    if reading.form == "keyword_list" and asks_why and grading.total > max_mark / 2:
        scale = (max_mark / 2) / grading.total
        scaled = [
            v.model_copy(update={"marks_awarded": round(v.marks_awarded * scale, 6)})
            for v in grading.verdicts
        ]
        return grading.model_copy(update={"verdicts": scaled}), "keyword_list_capped"
    return grading, None


def finalise_deductions(grading: Grading, rubric: Rubric, answer: str) -> tuple[Grading, list[str]]:
    """Keep only deductions that exist in the scheme, are quoted from the answer, and appear once.

    Marks come from the rule, not from the model. A deduction without a real quote is dropped,
    because a mark should never be taken off for something the student did not write.
    """
    rules = {d.id: d for d in rubric.deductions}
    kept: list[Deducted] = []
    flags: list[str] = []
    for d in grading.deductions:
        rule = rules.get(d.rule_id)
        if rule is None or any(k.rule_id == d.rule_id for k in kept):
            continue
        if not evidence_in_answer(d.evidence, answer):
            flags.append(f"deduction_dropped:{d.rule_id}")
            continue
        kept.append(d.model_copy(update={"marks": rule.marks}))
        flags.append(f"deduction:{d.rule_id}")
    return grading.model_copy(update={"deductions": kept}), flags


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
        if marks > EPS and not v.evidence.strip() and len(words(answer)) <= SHORT_ANSWER_WORDS:
            # credit with no quote on a one-line answer: the answer is the evidence. (In past runs
            # such credit was mostly right; removing it raised the error from 0.26 to 0.63.)
            v = v.model_copy(update={"evidence": answer.strip()})
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
    return grading.model_copy(update={"verdicts": fixed}), flags


def snap_grading(grading: Grading, rubric: Rubric, step: float) -> Grading:
    """The last word on granularity: every awarded mark is a multiple of `step` (or the point's
    full marks), whatever an earlier stage did, such as the form gate scaling marks down."""
    full = {p.id: p.marks for p in rubric.points}
    verdicts = []
    for v in grading.verdicts:
        top = full.get(v.point_id, v.marks_awarded)
        marks = top if abs(v.marks_awarded - top) < EPS else to_step(v.marks_awarded, step, top)
        verdicts.append(v.model_copy(update={"marks_awarded": marks}))
    deductions = [
        d.model_copy(update={"marks": to_step(d.marks, step, d.marks)}) for d in grading.deductions
    ]
    return grading.model_copy(update={"verdicts": verdicts, "deductions": deductions})

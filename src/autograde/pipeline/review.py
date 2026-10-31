"""Which marked answers are worth a person's look. Optional: the marks stand without it.

A reason is listed only where a look is likely to help. Reasons were chosen from the error of
flagged answers against the rest over past runs (DESIGN.md section 25): a mark that needed a
second try, a scheme that failed its own test, credit with no quote on a long answer, two markers
that disagree, a drawing or a handwritten word that could not be checked, and a partly right
answer whose total falls in the middle where the marker had to pick a level. Empty and nonsense
answers are not listed: they were marked right every time.
"""

from __future__ import annotations

from collections.abc import Sequence

from autograde.schemas import Result

LABELS = {
    "marking_unstable": "The marker gave an unclear answer first and had to be asked again.",
    "scheme_unreliable": "The marking scheme for this question did not pass its own check.",
    "credit_unquoted": "Marks were given, but the words that earned them are not in the answer.",
    "models_disagree": "Two markers gave different marks.",
    "form_or_deduction": "A rule lowered the mark (for example a missing unit).",
    "ocr_unsure": "The handwriting was hard to read in this answer.",
    "figure_unchecked": "A drawing could not be checked.",
    "ambiguous_partial": "The answer is partly right, so the exact mark was a close call.",
}
MID = (0.3, 0.7)  # share of the total that counts as mid-range
PARTIAL_WEIGHT = 0.2  # partial credit must be worth this share of the total to be a close call


def review_reasons(r: Result) -> list[str]:
    """Reasons a person might look at this result; empty when none apply."""
    kinds = {f.split(":")[0] for f in r.flags}
    if kinds & {"empty_answer", "incoherent_answer"}:
        return []
    out = []
    if kinds & {"retried", "repaired"}:
        out.append("marking_unstable")
    if "scheme_failed_selftest" in kinds:
        out.append("scheme_unreliable")
    if "unverified_quote" in kinds:
        out.append("credit_unquoted")
    if kinds & {"models_disagree", "escalated"}:
        out.append("models_disagree")
    if kinds & {"keyword_list_capped", "deduction"}:
        out.append("form_or_deduction")
    if "[?" in r.item.student_answer:
        out.append("ocr_unsure")
    if kinds & {"figure_missing", "figure_not_checked"}:
        out.append("figure_unchecked")
    if r.grading and r.item.max_mark > 0:
        share = r.predicted_mark / r.item.max_mark
        partial = sum(v.marks_awarded for v in r.grading.verdicts if v.status == "partial")
        if MID[0] <= share <= MID[1] and partial >= PARTIAL_WEIGHT * r.item.max_mark:
            out.append("ambiguous_partial")
    return out


BAD = 0.25  # error of this share of the total or more counts as badly marked


def review_stats(results: Sequence[Result]) -> dict:
    """Summarise the review list.

    Gives how many answers are listed, per reason, and (when the teacher's marks are known) whether
    the listed ones really are the worse-marked: their error against the rest, and the share of
    all badly marked answers they contain.
    """
    rows = [(review_reasons(r), r) for r in results]
    n = len(rows)
    listed = [r for reasons, r in rows if reasons]
    out: dict = {
        "n": n,
        "listed": len(listed),
        "listed_share": round(len(listed) / n, 3) if n else None,
        "by_reason": {k: sum(k in reasons for reasons, _ in rows) for k in LABELS},
    }
    marked = [(bool(reasons), r) for reasons, r in rows if r.item.human_mark is not None]
    if not marked:
        return out

    def err(r: Result) -> float:
        return abs(r.predicted_mark - r.item.human_mark) / r.item.max_mark

    hit = [err(r) for flagged, r in marked if flagged]
    rest = [err(r) for flagged, r in marked if not flagged]
    bad = sum(e >= BAD for e in hit + rest)
    out["error_listed"] = round(sum(hit) / len(hit), 3) if hit else None
    out["error_not_listed"] = round(sum(rest) / len(rest), 3) if rest else None
    out["bad_among_listed"] = round(sum(e >= BAD for e in hit) / len(hit), 3) if hit else None
    out["bad_among_not_listed"] = (
        round(sum(e >= BAD for e in rest) / len(rest), 3) if rest else None
    )
    out["share_of_bad_caught"] = round(sum(e >= BAD for e in hit) / bad, 3) if bad else None
    return out

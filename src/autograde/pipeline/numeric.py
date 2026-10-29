"""Numbers and units, checked by code. The model never does this arithmetic.

A final answer is compared with the expected value after converting units (150 cm matches 1.5 m,
1.5 km does not), within a tolerance. The check says whether the number is right and whether the
unit is right, missing or wrong, so the marks can separate a wrong result from a forgotten unit.
"""

from __future__ import annotations

import math
import re
import unicodedata
from dataclasses import dataclass

from autograde.schemas import EPS, Grading, NumericSpec, PointVerdict, Rubric

_NONE = (0,) * 7
# symbol -> (factor to SI, dimensions as exponents of m, kg, s, A, K, mol, cd). Case matters:
# N is newton, m is metre, h is hour, H is henry.
_UNITS: dict[str, tuple[float, tuple[int, ...]]] = {
    "m": (1, (1, 0, 0, 0, 0, 0, 0)),
    "g": (1e-3, (0, 1, 0, 0, 0, 0, 0)),
    "s": (1, (0, 0, 1, 0, 0, 0, 0)),
    "A": (1, (0, 0, 0, 1, 0, 0, 0)),
    "K": (1, (0, 0, 0, 0, 1, 0, 0)),
    "mol": (1, (0, 0, 0, 0, 0, 1, 0)),
    "min": (60, (0, 0, 1, 0, 0, 0, 0)),
    "h": (3600, (0, 0, 1, 0, 0, 0, 0)),
    "hr": (3600, (0, 0, 1, 0, 0, 0, 0)),
    "L": (1e-3, (3, 0, 0, 0, 0, 0, 0)),
    "l": (1e-3, (3, 0, 0, 0, 0, 0, 0)),
    "Hz": (1, (0, 0, -1, 0, 0, 0, 0)),
    "N": (1, (1, 1, -2, 0, 0, 0, 0)),
    "Pa": (1, (-1, 1, -2, 0, 0, 0, 0)),
    "bar": (1e5, (-1, 1, -2, 0, 0, 0, 0)),
    "atm": (101325, (-1, 1, -2, 0, 0, 0, 0)),
    "J": (1, (2, 1, -2, 0, 0, 0, 0)),
    "cal": (4.184, (2, 1, -2, 0, 0, 0, 0)),
    "eV": (1.602176634e-19, (2, 1, -2, 0, 0, 0, 0)),
    "Wh": (3600, (2, 1, -2, 0, 0, 0, 0)),
    "W": (1, (2, 1, -3, 0, 0, 0, 0)),
    "C": (1, (0, 0, 1, 1, 0, 0, 0)),
    "V": (1, (2, 1, -3, -1, 0, 0, 0)),
    "ohm": (1, (2, 1, -3, -2, 0, 0, 0)),
    "Ω": (1, (2, 1, -3, -2, 0, 0, 0)),
    "F": (1, (-2, -1, 4, 2, 0, 0, 0)),
    "H": (1, (2, 1, -2, -2, 0, 0, 0)),
    "T": (1, (0, 1, -2, -1, 0, 0, 0)),
    "%": (0.01, _NONE),
    "rad": (1, _NONE),
    "deg": (math.pi / 180, _NONE),
    "°": (math.pi / 180, _NONE),
}
_BY_LOWER = {k.lower(): k for k in _UNITS if k not in {"m", "h", "H", "l", "L", "T", "K", "A"}}
_PREFIX = {
    "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "μ": 1e-6, "m": 1e-3, "c": 1e-2, "d": 1e-1,
    "k": 1e3, "M": 1e6, "G": 1e9, "T": 1e12,
}  # fmt: skip
_POWERS = {"²": "^2", "³": "^3", "⁻¹": "^-1", "⁻²": "^-2", "¹": "^1"}
_NUM = (
    r"(?P<num>[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?|[-+]?\d+(?:[.,]\d+)?)"
    r"(?:\s*(?:[eE]\s*(?P<e>[-+]?\d+)|[x×*·]\s*10\s*\^?\s*(?P<p>[-+]?\d+)))?"
)
_UNIT = r"(?:\s*(?P<unit>[A-Za-zµμΩω°%][^\s,;:()=]*))?"
_NUMBER = re.compile(_NUM + _UNIT)


def _clean(text: str) -> str:
    for sup, plain in _POWERS.items():  # before NFKC, which would flatten ² to a plain 2
        text = text.replace(sup, plain)
    return unicodedata.normalize("NFKC", text).replace("−", "-")


def _atom(token: str) -> tuple[float, tuple[int, ...]] | None:
    """One unit symbol such as km, mm, N, kΩ or %, with its prefix; exact case first."""
    if token in _UNITS:
        return _UNITS[token]
    if len(token) >= 2 and token.lower() in _BY_LOWER:  # KG, Hz written as HZ, ...
        return _UNITS[_BY_LOWER[token.lower()]]
    if len(token) >= 2 and token[0] in _PREFIX:
        base = _atom(token[1:])
        if base:
            return base[0] * _PREFIX[token[0]], base[1]
    return None


def parse_unit(text: str) -> tuple[float, tuple[int, ...]] | None:
    """Factor to SI and dimensions of a compound unit like m/s^2 or kg*m/s^2; None if unknown."""
    text = _clean(text).strip().strip(".")
    if not text:
        return 1.0, _NONE
    factor, dims = 1.0, [0] * 7
    sign = 1
    for part in re.split(r"([/*·])", text):
        if part == "/":
            sign = -1
            continue
        part = part.strip()
        if not part or part in "*·":
            continue
        match = re.fullmatch(r"([^^]+?)(?:\^\(?(-?\d+)\)?)?", part)
        if not match:
            return None
        atom = _atom(match.group(1))
        if atom is None:
            return None
        power = int(match.group(2) or 1) * sign
        factor *= atom[0] ** power
        dims = [d + power * a for d, a in zip(dims, atom[1], strict=True)]
    return factor, tuple(dims)


@dataclass
class Candidate:
    value: float
    unit: str


def find_numbers(text: str) -> list[Candidate]:
    """Every number in the text with the unit written right after it, in reading order."""
    out = []
    for m in _NUMBER.finditer(_clean(text)):
        num = m.group("num")
        raw = num.replace(",", "") if re.search(r",\d{3}", num) else num.replace(",", ".")
        try:
            value = float(raw)
        except ValueError:
            continue
        exp = m.group("e") if m.group("e") is not None else m.group("p")
        if exp is not None:
            value *= 10 ** int(exp)
        out.append(Candidate(value, (m.group("unit") or "").rstrip(".")))
    return out


_CLAIMS_NO_UNIT = re.compile(
    r"\bunits?\b.{0,40}\b(missing|lack\w*|absent|omitted|without)\b"
    r"|\b(missing|lack\w*|no|without|omitted)\b.{0,25}\bunits?\b",
    re.IGNORECASE,
)


@dataclass
class NumericResult:
    found: bool  # some number was written
    value_ok: bool
    unit: str  # ok | missing | wrong | not_needed
    seen: str  # the number that matched (or came closest), as written
    final: str = ""  # the last number written, as written
    final_unit: str = ""  # whether that last number has the right unit: ok | missing | wrong


def _close(a: float, b: float, spec: NumericSpec) -> bool:
    return abs(a - b) <= max(spec.rel_tol * abs(b), spec.abs_tol, EPS)


def check_number(answer: str, spec: NumericSpec) -> NumericResult:
    """Compare the numbers in `answer` with the expected value, converting units.

    The last matching number counts first (a worked solution ends with its answer). A number
    that matches in value but has a missing or wrong unit is reported as such, not as a wrong
    value.
    """
    expected = parse_unit(spec.unit) if spec.unit else (1.0, _NONE)
    candidates = find_numbers(answer)
    no_unit = "missing" if spec.unit else "not_needed"
    if not candidates:
        return NumericResult(False, False, no_unit, "")
    last = candidates[-1]
    last_unit = _unit_state(last.unit, spec.unit, expected)
    best = NumericResult(True, False, no_unit, "", f"{last.value:g} {last.unit}".strip(), last_unit)
    for cand in reversed(candidates):
        written = f"{cand.value:g} {cand.unit}".strip()
        right_number = _close(cand.value, spec.value, spec)
        if not spec.unit:
            if right_number:
                return NumericResult(True, True, "not_needed", written)
            continue
        if not cand.unit:
            if right_number and not best.value_ok:
                best = NumericResult(True, True, "missing", written)
            continue
        got = parse_unit(cand.unit)
        if got is None or expected is None:  # a unit we do not know: only the same text counts
            if right_number and cand.unit.lower() == spec.unit.lower():
                return NumericResult(True, True, "ok", written)
            if right_number and not best.value_ok:
                best = NumericResult(True, True, "wrong", written)
        elif got[1] == expected[1]:  # same kind of unit: convert into the expected one
            if _close(cand.value * got[0] / expected[0], spec.value, spec):
                return NumericResult(True, True, "ok", written)
        elif right_number and not best.value_ok:
            best = NumericResult(True, True, "wrong", written)
    return best


def _unit_state(written: str, wanted: str, expected: tuple[float, tuple[int, ...]] | None) -> str:
    """Is the unit written after a number the right kind of unit: ok, missing or wrong."""
    if not wanted:
        return "not_needed"
    if not written:
        return "missing"
    got = parse_unit(written)
    if got is None or expected is None:
        return "ok" if written.lower() == wanted.lower() else "wrong"
    return "ok" if got[1] == expected[1] else "wrong"


def describe_result(spec: NumericSpec, res: NumericResult) -> str:
    want = f"{spec.value:g} {spec.unit}".strip()
    tol = f"{spec.rel_tol:.0%} tolerance" if spec.rel_tol else f"within {spec.abs_tol:g}"
    if not res.found:
        return f"Expected final answer {want} ({tol}). No number was found in the answer."
    if not res.value_ok:
        said = {
            "ok": "its unit is right",
            "missing": "it has no unit",
            "wrong": "its unit is wrong",
            "not_needed": "no unit is needed",
        }.get(res.final_unit, "")
        last = f" The last number written is {res.final}; {said}." if res.final else ""
        return f"Expected final answer {want} ({tol}). The numbers written do not match it.{last}"
    unit = {
        "ok": "the unit is right",
        "missing": "the unit is missing",
        "wrong": "the unit is wrong",
        "not_needed": "no unit is needed",
    }[res.unit]
    return f"Expected final answer {want} ({tol}). Matches: {res.seen}; {unit}."


def decide_numeric(
    grading: Grading, rubric: Rubric, answer: str, follow_through: bool = False
) -> tuple[Grading, str, list[str]]:
    """Settle every point that has a numeric spec. Returns the grading, a note for the marker
    and flags. Value right and unit right: full marks. Value right, unit missing or wrong: the
    unit share is lost. Value wrong or absent: nothing for this point, except under
    `follow_through`, where the number may differ because of the student's own earlier result:
    the marker's verdict then stands and the answer is flagged for the teacher."""
    notes, flags = [], []
    verdicts = {v.point_id: v for v in grading.verdicts}
    for point in rubric.points:
        if point.numeric is None or point.id not in verdicts:
            continue
        res = check_number(answer, point.numeric)
        text = describe_result(point.numeric, res)
        notes.append(f"{point.id}: {text}")
        if res.value_ok and res.unit in ("ok", "not_needed"):
            status, marks = "met", point.marks
        elif res.value_ok:
            status, marks = "partial", round(point.marks * (1 - point.numeric.unit_share), 6)
            flags.append(f"unit_{res.unit}:{point.id}")
        elif follow_through and res.found:
            flags.append(f"follow_through_unchecked:{point.id}")
            old = verdicts[point.id]
            if res.final_unit == "ok" and _CLAIMS_NO_UNIT.search(old.reason):
                # the marker's verdict stands, but not its false claim about the unit
                verdicts[point.id] = old.model_copy(update={"reason": text})
                flags.append(f"reason_corrected:{point.id}")
            continue
        else:
            status, marks = "not_met", 0.0
        old = verdicts[point.id]
        verdicts[point.id] = PointVerdict(
            point_id=point.id,
            status=status,
            marks_awarded=marks,
            model_marks=old.model_marks if old.model_marks is not None else old.marks_awarded,
            evidence=res.seen if status != "not_met" else "",
            reason=text,
        )
    out = [verdicts[v.point_id] for v in grading.verdicts]
    return grading.model_copy(update={"verdicts": out}), "\n".join(notes), flags


def numeric_notes(rubric: Rubric, answer: str, follow_through: bool = False) -> str:
    """What the code found for each numeric point, as facts for the marker before it marks."""
    lines = []
    for p in rubric.points:
        if p.numeric is not None:
            res = check_number(answer, p.numeric)
            line = f"{p.id}: {describe_result(p.numeric, res)}"
            if follow_through and res.found and not res.value_ok:
                line += (
                    " This part builds on the student's earlier parts, so a different number may "
                    "be correct: judge it from the student's own earlier result, not from this "
                    "check."
                )
            lines.append(line)
    return "\n".join(lines)

"""Who wrote an answer sheet, read from the sheet itself and checked against the student directory.

The file name is not trusted: scans arrive as `IMG_0042.pdf`, `final.docx`. The roll number written
on the sheet is the primary identifier; the name written beside it settles doubt. The directory
(the app's student database, or a roster CSV) is what makes this reliable rather than a guess:

1. Read the header of the sheet. A labelled roll number or name is taken as written, and any known
   roll number that appears in the header is found even without a label.
2. Match the roll number against the directory. An exact match is accepted (checked against the
   name if there is one). A roll number off by one character (a mis-read or mistyped digit) is
   corrected only if exactly one student is that close, or the name picks one of several.
3. With no usable roll number, match the name, preferring students enrolled in the exam's course.
   A single clear match is accepted but flagged for a check.
4. Only if that is still ambiguous is the model shown the header and the few candidate students
   from the directory, and asked to choose among them. Code rejects any answer not in that list.
5. What is left goes to the teacher, with the candidates, and never guesses.

Every result says how it was reached (`method`) and what to look at (`flags`); `status` is `ok`
(roll number and name agree), `check` (resolved, but a person should glance at it) or
`unresolved`. Pure code except steps 1's optional extraction and 4, which take a client.
"""

from __future__ import annotations

import re
import sqlite3
import unicodedata
from collections.abc import Iterable
from dataclasses import asdict, dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.llm import LLMClient

NAME_OK = 0.80  # the name on the sheet matches the directory's well enough to confirm the roll
NAME_BAD = 0.50  # below this the name contradicts the roll number
NAME_PICK = 0.75  # the least a name must score to be proposed on its own
MARGIN = 0.10  # how far the best name must beat the second to be accepted
MAX_CANDIDATES = 8
HEADER_CHARS = 1200

_ROLL = re.compile(
    r"(?im)\b(?:roll|reg(?:istration)?|enrol(?:l)?ment|student)\s*(?:no\.?|number|id|#)?\s*[:=\-–]\s*(.+)"
)
_NAME = re.compile(r"(?im)\bname\s*[:=\-–]\s*(.+)")
_FIRST_QUESTION = re.compile(r"(?im)^\s*(?:q(?:uestion)?\s*\.?\s*)?1\s*[.):]|^\s*q\s*1\b")


@dataclass(frozen=True)
class Person:
    """A student in the directory: id, name and whether enrolled in the exam's course."""

    student_id: str
    name: str = ""
    enrolled: bool = True  # in the exam's course; True for a directory with no course information


@dataclass(frozen=True)
class Claim:
    """What the sheet says about its author, as written (may be empty or misspelt)."""

    roll: str = ""
    name: str = ""


@dataclass
class Resolution:
    """How one answer sheet was attributed to a student, and how sure that is."""

    source: str  # the file
    student_id: str | None
    method: str  # roll, roll+name, roll_corrected, name, model, filename, teacher, none
    status: str  # ok, check, unresolved
    flags: list[str] = field(default_factory=list)
    claimed: Claim = field(default_factory=Claim)
    name: str = ""  # the directory's name for the student
    candidates: list[dict] = field(default_factory=list)  # who it might be, when unresolved

    def to_dict(self) -> dict:
        """Return the resolution as a plain dict."""
        return asdict(self)


# ---------- the directory ----------


def load_directory(path: Path, course_id: int | None = None) -> list[Person]:
    """Read the students from the app's database or from a roster CSV.

    The database is opened read-only (tables `students` and `enrolments`); a roster has the
    columns `student_id` and `name`. With a course id, `enrolled` says who is in it; a course
    nobody is enrolled in yet counts everyone as enrolled.
    """
    if path.suffix.lower() in {".db", ".sqlite", ".sqlite3"}:
        conn = sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)
        try:
            rows = conn.execute(
                "SELECT student_id, name FROM students ORDER BY student_id"
            ).fetchall()
            enrolled = None
            if course_id is not None:
                enrolled = {
                    r[0]
                    for r in conn.execute(
                        "SELECT student_id FROM enrolments"
                        " WHERE course_id = ? AND status = 'active'",
                        (course_id,),
                    )
                }
        finally:
            conn.close()
        if not enrolled:  # an empty roster is no information, not a class of nobody
            enrolled = None
        return [Person(sid, name, enrolled is None or sid in enrolled) for sid, name in rows]
    import csv

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = {(c or "").strip().lower(): c for c in reader.fieldnames or []}
        id_col = next(
            (fields[c] for c in ("student_id", "id", "roll", "roll_no") if c in fields), None
        )
        if id_col is None:
            raise ValueError(f"{path.name} needs a student_id column.")
        name_col = fields.get("name")
        return [
            Person(row[id_col].strip(), (row.get(name_col) or "").strip() if name_col else "")
            for row in reader
            if (row.get(id_col) or "").strip()
        ]


def load_directories(paths: Iterable[Path], course_id: int | None = None) -> list[Person]:
    """Merge several directories into one.

    For example the database and the roster the teacher uploaded with the sheets (who may not
    be in the database yet). The first source wins where they overlap; later ones only add
    students, or a name the first lacked.
    """
    merged: dict[str, Person] = {}
    for path in paths:
        for p in load_directory(path, course_id):
            key = norm_id(p.student_id)
            known = merged.get(key)
            if known is None:
                merged[key] = p
            elif not known.name and p.name:
                merged[key] = Person(known.student_id, p.name, known.enrolled)
    return list(merged.values())


# ---------- matching ----------


def norm_id(text: str) -> str:
    """Case, spaces, dashes and dots do not matter: 's24 001' and 'S24-001' are S24001."""
    return re.sub(r"[^A-Z0-9]", "", unicodedata.normalize("NFC", text).upper())


def _tokens(name: str) -> list[str]:
    name = unicodedata.normalize("NFC", name).casefold()
    name = re.sub(r"\b(?:mr|mrs|ms|miss|dr|shri|smt)\b\.?", " ", name)
    return [t for t in re.split(r"[^\w]+", name) if t]


def name_score(a: str, b: str) -> float:
    """Score from 0 to 1 how likely two spellings are the same person.

    Word order and spelling slips do not matter; 'Asha' alone fits 'Asha Rao' (but fits every
    Asha equally).
    """
    ta, tb = _tokens(a), _tokens(b)
    if not ta or not tb:
        return 0.0
    fuzzy = SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()
    contained = 0.9 if set(ta) <= set(tb) or set(tb) <= set(ta) else 0.0
    return max(fuzzy, contained)


def edit_distance(a: str, b: str) -> int:
    """Return the number of single-character edits between two strings."""
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _ranked(name: str, pool: Iterable[Person]) -> list[tuple[float, Person]]:
    return sorted(((name_score(name, p.name), p) for p in pool if p.name), key=lambda t: -t[0])


def _candidates(name: str, people: list[Person]) -> list[dict]:
    pool = [p for p in people if p.enrolled] or people
    return [
        {"student_id": p.student_id, "name": p.name, "score": round(s, 2)}
        for s, p in _ranked(name, pool)[:5]
        if s >= 0.5
    ]


def resolve(
    claim: Claim, stem: str, people: list[Person], taken: Iterable[str] = (), source: str = ""
) -> Resolution:
    """Decide who a sheet belongs to from what it claims and what the directory knows. Pure code."""
    by_id = {norm_id(p.student_id): p for p in people}
    stem_person = by_id.get(norm_id(stem))
    flags: list[str] = []
    chosen: Person | None = None
    method, status = "none", "ok"
    candidates: list[dict] = []

    roll = norm_id(claim.roll)
    if roll in by_id:  # an exact roll number is the strongest evidence
        chosen, method = by_id[roll], "roll"
        if claim.name and chosen.name:
            score = name_score(claim.name, chosen.name)
            if score >= NAME_OK:
                method = "roll+name"
            elif score < NAME_BAD:
                flags.append("name_mismatch")
                status = "check"
    elif len(roll) >= 4:  # a roll number off by one character: a slip, or a mis-read digit
        near = [
            p
            for k, p in by_id.items()
            if abs(len(k) - len(roll)) <= 1 and edit_distance(k, roll) <= 1
        ]
        if len(near) == 1:
            chosen = near[0]
        elif len(near) > 1 and claim.name:
            ranked = _ranked(claim.name, near)
            if ranked[0][0] >= NAME_PICK and ranked[0][0] - ranked[1][0] >= MARGIN:
                chosen = ranked[0][1]
        if chosen:
            method, status = "roll_corrected", "check"
            flags.append(f"roll_corrected:{claim.roll.strip()}->{chosen.student_id}")
        elif roll:
            flags.append(f"unknown_roll:{claim.roll.strip()}")

    if chosen is None and claim.name:  # no usable roll number: the name, among the enrolled first
        pool = [p for p in people if p.enrolled]
        ranked = _ranked(claim.name, pool)
        if not ranked or ranked[0][0] < NAME_PICK:
            ranked = _ranked(claim.name, people)
        clear = len(ranked) == 1 or (len(ranked) > 1 and ranked[0][0] - ranked[1][0] >= MARGIN)
        if ranked and ranked[0][0] >= NAME_PICK and clear:
            chosen, method, status = ranked[0][1], "name", "check"
            flags.append("matched_by_name")
        if chosen is None:
            candidates = _candidates(claim.name, people)

    if chosen is None and stem_person is not None:  # nothing on the sheet: the file name is a hint
        chosen, method, status = stem_person, "filename", "check"
        flags.append("from_filename")
    elif chosen is not None and stem_person is not None and stem_person is not chosen:
        flags.append(f"filename_conflict:{stem_person.student_id}")  # the sheet wins over the name
        status = "check"

    if chosen is None:
        return Resolution(
            source, None, "none", "unresolved", flags or ["no_identity"], claim, "", candidates
        )
    if not chosen.enrolled:
        flags.append("not_enrolled")
        status = "check"
    if norm_id(chosen.student_id) in {norm_id(t) for t in taken}:
        return Resolution(
            source, None, method, "unresolved", [*flags, f"duplicate:{chosen.student_id}"], claim,
            chosen.name, [{"student_id": chosen.student_id, "name": chosen.name, "score": 1.0}],
        )  # fmt: skip
    return Resolution(source, chosen.student_id, method, status, flags, claim, chosen.name)


# ---------- reading the sheet ----------


def header_of(text: str) -> str:
    """The top of the sheet, up to the first question."""
    head = text[:HEADER_CHARS]
    first = _FIRST_QUESTION.search(head)
    return head[: first.start()] if first and first.start() > 0 else head


def _clean(value: str) -> str:
    return re.split(r"(?i)\s+name\b|\s{2,}|[,;|]", value.strip())[0].strip()


def claim_from_header(header: str, people: list[Person]) -> Claim:
    """Read the roll number and name as written, by their labels.

    Failing a labelled roll number, any known roll number found in the header is used.
    """
    roll_match, name_match = _ROLL.search(header), _NAME.search(header)
    roll = _clean(roll_match.group(1)) if roll_match else ""
    name = _clean(name_match.group(1)) if name_match else ""
    if not roll:
        squashed = norm_id(header)
        known = [
            p.student_id
            for p in people
            if len(norm_id(p.student_id)) >= 5 and norm_id(p.student_id) in squashed
        ]
        roll = known[0] if len(known) == 1 else ""
    return Claim(roll, name)


class _Claimed(BaseModel):
    roll_number: str = ""
    name: str = ""


class _Pick(BaseModel):
    student_id: str = "none"
    reason: str = ""


def extract_claim(header: str, client: LLMClient) -> Claim:
    """Ask the model to copy out the roll number and name, for headers the labels did not parse."""
    got = client.ask(prompts.system("intake.identity"), header, _Claimed)
    return Claim(got.roll_number.strip(), got.name.strip())


def pick_candidate(header: str, candidates: list[Person], client: LLMClient) -> Person | None:
    """Let the model choose among real candidates from the directory.

    Its answer is accepted only if it names one of them.
    """
    listing = "\n".join(f"{p.student_id}: {p.name}" for p in candidates)
    user = f"HEADER:\n{header}\n\nCANDIDATES:\n{listing}"
    got = client.ask(prompts.system("intake.identity_pick"), user, _Pick)
    by_id = {norm_id(p.student_id): p for p in candidates}
    return by_id.get(norm_id(got.student_id))


def identify(
    source: str,
    text: str,
    people: list[Person],
    client: LLMClient | None = None,
    taken: Iterable[str] = (),
    fixes: dict[str, str] | None = None,
) -> Resolution:
    """The whole procedure for one sheet. A teacher's fix for this file overrides everything."""
    stem = Path(source).stem
    by_id = {norm_id(p.student_id): p for p in people}
    fixed = by_id.get(norm_id((fixes or {}).get(source, "")))
    if fixed is not None:
        return Resolution(source, fixed.student_id, "teacher", "ok", [], Claim(), fixed.name)
    header = header_of(text)
    claim = claim_from_header(header, people)
    result = resolve(claim, stem, people, taken, source)
    if result.status != "unresolved" or client is None:
        return result
    if any(f.startswith("duplicate:") for f in result.flags):
        return result  # a second sheet for the same student is for a person to look at
    if not (claim.roll and claim.name):  # labels missed something: let the model copy it out
        got = extract_claim(header, client)
        claim = Claim(claim.roll or got.roll, claim.name or got.name)
        result = resolve(claim, stem, people, taken, source)
        if result.status != "unresolved":
            result.flags.append("claim_read_by_model")
            result.status = "check"
            return result
    pool = {c["student_id"] for c in result.candidates}  # only real candidates, never "everyone"
    shortlist = [p for p in people if p.student_id in pool][:MAX_CANDIDATES]
    chosen = pick_candidate(header, shortlist, client) if shortlist else None
    if chosen is not None and norm_id(chosen.student_id) not in {norm_id(t) for t in taken}:
        flags = [*result.flags, "model_chose"]
        return Resolution(source, chosen.student_id, "model", "check", flags, claim, chosen.name)
    result.claimed = claim
    return result

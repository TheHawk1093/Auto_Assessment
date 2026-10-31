"""Student answers: typed files, a JSON file, or sheets read by `autograde ocr`."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

from pydantic import BaseModel

from autograde import prompts
from autograde.intake.figures import anchor_figures
from autograde.intake.files import read_document
from autograde.intake.identity import Claim, Person, Resolution, identify, resolve
from autograde.intake.models import Paper
from autograde.llm import LLMClient
from autograde.ocr.sheets import Sheet

Answers = dict[str, dict[str, str]]  # student -> question id -> text


class _Split(BaseModel):
    answers: dict[str, str]


def norm(qid: str) -> str:
    """'Q2(a)', '2.a' and '2a' are the same question."""
    return re.sub(r"^(?:question|q)", "", re.sub(r"[^a-z0-9]", "", qid.lower()))


def load_answers(
    path: Path, paper: Paper, client: LLMClient | None = None
) -> tuple[Answers, list[str]]:
    """Read the answers of every student.

    Args:
        path: A folder (one file per student, or the output folder of `autograde ocr`) or one
            JSON file {student: {question id: text}}.
        paper: The question paper the answers belong to.
        client: Model used to split text where no question markers are found.

    Returns:
        The answers per student, and warnings.
    """
    warnings: list[str] = []
    answers: Answers = {}
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        data = data.get("students", data)
        for student, per_q in data.items():
            per_q = {q: anchor_figures(str(t), path.parent) for q, t in per_q.items()}
            answers[str(student)] = _match(per_q, paper, f"{student}", warnings)
        return answers, warnings
    for file in sorted(path.iterdir()):
        if file.name.endswith(".sheet.json"):
            sheet = Sheet.model_validate_json(file.read_text(encoding="utf-8"))
            per_q = {it.question_id: it.student_answer for it in sheet.items}
            name = sheet.student or sheet.sheet or file.name.removesuffix(".sheet.json")
            answers[name] = _match(per_q, paper, name, warnings)
        elif file.suffix.lower() in {".txt", ".md", ".docx", ".pdf"}:
            per_q = split_text(read_document(file), paper, client)
            answers[file.stem] = _match(per_q, paper, file.stem, warnings)
    if not answers:
        warnings.append(f"No answer files found in {path}.")
    return answers, warnings


def load_answers_identified(
    path: Path,
    paper: Paper,
    client: LLMClient | None,
    people: list[Person],
    fixes: dict[str, str] | None = None,
) -> tuple[Answers, list[str], list[Resolution]]:
    """Read the answers like `load_answers`, attributing each sheet by what it says.

    The roll number is tried first, then the name, checked against the student directory; the
    file name is not used. A sheet that cannot be attributed with confidence is left out of the
    answers; its resolution says why and who it might be.

    Args:
        path: As for `load_answers`.
        paper: The question paper the answers belong to.
        client: Model used to split text and to pick among candidate students.
        people: The student directory.
        fixes: Maps a file name to the student id a teacher has chosen for it.

    Returns:
        The answers keyed by student id, warnings, and one `Resolution` per sheet.
    """
    if path.is_file():  # one JSON keyed by student id: nothing to identify
        answers, warnings = load_answers(path, paper, client)
        return answers, warnings, []
    warnings: list[str] = []
    entries: list[tuple[Resolution, str | dict[str, str]]] = []  # (who, the text or its answers)
    for file in sorted(path.iterdir()):
        if file.name.endswith(".sheet.json"):
            sheet = Sheet.model_validate_json(file.read_text(encoding="utf-8"))
            who = sheet.student or sheet.sheet or file.name.removesuffix(".sheet.json")
            res = resolve(
                Claim(who, who), file.name.removesuffix(".sheet.json"), people, (), file.name
            )
            if (fixes or {}).get(file.name):
                res = identify(file.name, "", people, None, (), fixes)
            entries.append((res, {it.question_id: it.student_answer for it in sheet.items}))
        elif file.suffix.lower() in {".txt", ".md", ".docx", ".pdf"}:
            text = read_document(file)
            entries.append((identify(file.name, text, people, client, (), fixes), text))
    _hold_duplicates(entries)
    answers: Answers = {}
    resolutions: list[Resolution] = []
    for res, payload in entries:
        resolutions.append(res)
        if not res.student_id:
            warnings.append(
                f"{res.source}: could not tell which student wrote this ({', '.join(res.flags)})."
            )
            continue
        per_q = payload if isinstance(payload, dict) else split_text(payload, paper, client)
        answers[res.student_id] = _match(per_q, paper, res.student_id, warnings)
    if not answers:
        warnings.append(f"No answer files found in {path}.")
    return answers, warnings, resolutions


def _hold_duplicates(entries: list[tuple[Resolution, object]]) -> None:
    """Hold both sheets when two are attributed to one student.

    Nobody can tell which is the real one, so both are held for a person, unless a teacher has
    already settled exactly one of them.
    """
    by_student: dict[str, list[int]] = {}
    for i, (res, _) in enumerate(entries):
        if res.student_id:
            by_student.setdefault(res.student_id, []).append(i)
    for sid, group in by_student.items():
        if len(group) < 2:
            continue
        settled = [i for i in group if entries[i][0].method == "teacher"]
        for i in group:
            if len(settled) == 1 and i == settled[0]:
                continue
            res, payload = entries[i]
            held = Resolution(
                res.source, None, res.method, "unresolved", [*res.flags, f"duplicate:{sid}"],
                res.claimed, res.name, [{"student_id": sid, "name": res.name, "score": 1.0}],
            )  # fmt: skip
            entries[i] = (held, payload)


def _match(
    per_q: dict[str, str], paper: Paper, student: str, warnings: list[str]
) -> dict[str, str]:
    """Map a student's answers onto the paper's question ids, joining repeats."""
    by_norm = {norm(q.id): q.id for q in paper.questions}
    out: dict[str, str] = {}
    for qid, text in per_q.items():
        target = by_norm.get(norm(str(qid)))
        if target is None:
            if text.strip():
                warnings.append(f"{student}: answer to unknown question {qid!r} was ignored.")
            continue
        out[target] = f"{out[target]}\n{text}".strip() if target in out else text.strip()
    blank = [q.id for q in paper.questions if not out.get(q.id)]
    if blank:
        warnings.append(f"{student}: no answer found for {', '.join(blank)}.")
    return out


def _marker(qid: str) -> re.Pattern[str]:
    """A line that starts the answer to `qid`: 'Q2a.', 'Answer 2(a):', '2 a)', '(2a)'."""
    parts = re.findall(r"\d+|[a-z]+", qid.lower())
    body = r"[ \t.\-(]*".join(re.escape(p) for p in parts)
    return re.compile(
        rf"^[ \t#*]*(?:question|ques|answer|ans|q|a)?[ \t.:#*\-]*\(?{body}\)?[ \t]*[.:)\-][ \t]*",
        re.IGNORECASE | re.MULTILINE,
    )


def split_text(text: str, paper: Paper, client: LLMClient | None = None) -> dict[str, str]:
    """Split one student's text into answers.

    Question markers are looked for first; when too few are found the model splits the text.
    """
    spots: list[tuple[int, int, str]] = []
    pos = 0
    for q in paper.questions:
        m = _marker(q.id).search(text, pos)
        if m:
            spots.append((m.start(), m.end(), q.id))
            pos = m.end()
    if len(spots) >= math.ceil(len(paper.questions) / 2) or client is None:
        out = {}
        for i, (_, end, qid) in enumerate(spots):
            stop = spots[i + 1][0] if i + 1 < len(spots) else len(text)
            out[qid] = text[end:stop].strip()
        return out
    listing = "\n".join(f"{q.id}: {q.text[:150]}" for q in paper.questions)
    user = f"Questions:\n{listing}\n\nStudent's text:\n{text}"
    return client.ask(prompts.system("intake.answers"), user, _Split).answers

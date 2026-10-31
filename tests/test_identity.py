"""Identity resolution: who wrote a sheet, from what it says, checked against the directory.

The roll number is primary and the name settles doubt; the file name is only a weak hint. Plain
code throughout, with a scripted model for the two places a model may help.
"""

from __future__ import annotations

import sqlite3

import pytest

from autograde.intake.answers import load_answers_identified
from autograde.intake.identity import (
    Claim,
    Person,
    _Claimed,
    _Pick,
    claim_from_header,
    edit_distance,
    header_of,
    identify,
    load_directories,
    load_directory,
    name_score,
    norm_id,
    resolve,
)
from autograde.intake.models import Paper, QuestionSpec
from fakes import FakeClient

PEOPLE = [
    Person("S24001", "Aarav Mehta"),
    Person("S24002", "Bhavna Iyer"),
    Person("S24003", "Chirag Nair"),
    Person("S24004", "Divya Menon"),
    Person("S24005", "Esha Kulkarni"),
    Person("S24009", "Anita Rao"),
    Person("S24010", "Anita Rane"),
    Person("S24011", "Kavya Shah"),
    Person("S24012", "Late Joiner", enrolled=False),
]


def sheet(header: str) -> str:
    return f"{header}\n\nQ1. The answer.\n\nQ2. Another."


# ---------- the building blocks ----------


def test_roll_numbers_ignore_case_spacing_and_punctuation():
    assert norm_id("s24 001") == norm_id("S24-001") == norm_id("S24.001") == "S24001"


def test_edit_distance():
    assert edit_distance("S24003", "S24O03") == 1 and edit_distance("S24001", "S24001") == 0
    assert edit_distance("S2401", "S24001") == 1 and edit_distance("abc", "xyz") == 3


def test_names_match_despite_order_titles_and_slips_but_not_other_people():
    assert name_score("Mehta Aarav", "Aarav Mehta") == 1.0
    assert name_score("Dr. Aarav Mehta", "Aarav Mehta") >= 0.9
    assert name_score("Chirag Nayar", "Chirag Nair") > 0.8
    assert name_score("Aarav Mehta", "Divya Menon") < 0.5
    assert name_score("", "Aarav") == 0.0


def test_the_header_stops_before_the_first_question():
    assert "Q1" not in header_of("Name: A\nRoll: S1\n\nQ1. answer here")
    assert header_of("Q1. no header at all").startswith("Q1")  # nothing to cut


@pytest.mark.parametrize(
    "header, roll, name",
    [
        ("Name: Aarav Mehta\nRoll No: S24001", "S24001", "Aarav Mehta"),
        ("Name - Bhavna Iyer   Reg. No: S24002", "S24002", "Bhavna Iyer"),
        ("Roll Number = S24 003 , Name: Chirag Nair", "S24 003", "Chirag Nair"),
        ("Student ID: S24004\nName : Divya Menon", "S24004", "Divya Menon"),
        ("Aarav Mehta   S24001   ME1001 Quiz", "S24001", ""),  # no labels: a known roll is found
        ("just some words", "", ""),
    ],
)
def test_the_claim_is_read_from_labels_or_a_known_roll_number(header, roll, name):
    claim = claim_from_header(header, PEOPLE)
    assert (claim.roll, claim.name) == (roll, name)


# ---------- resolving a claim ----------


def test_an_exact_roll_with_the_right_name_is_confirmed():
    r = resolve(Claim("S24001", "Aarav Mehta"), "scan_17", PEOPLE)
    assert (r.student_id, r.method, r.status, r.flags) == ("S24001", "roll+name", "ok", [])


def test_an_exact_roll_alone_is_accepted_without_fuss():
    r = resolve(Claim("s24 002", ""), "IMG_0042", PEOPLE)
    assert (r.student_id, r.method, r.status) == ("S24002", "roll", "ok")


def test_the_roll_is_primary_even_when_the_name_disagrees_but_it_is_flagged():
    r = resolve(Claim("S24001", "Divya Menon"), "x", PEOPLE)
    assert r.student_id == "S24001" and r.status == "check" and "name_mismatch" in r.flags


def test_a_misread_digit_is_corrected_when_only_one_student_is_that_close():
    r = resolve(Claim("S24O03", "Chirag Nair"), "x", PEOPLE)  # letter O for zero
    assert (r.student_id, r.method, r.status) == ("S24003", "roll_corrected", "check")
    assert r.flags == ["roll_corrected:S24O03->S24003"]


def test_when_two_students_are_equally_close_the_name_decides():
    # 'S2401' is one edit from S24001 (Aarav) and S24011 (Kavya)
    r = resolve(Claim("S2401", "Kavya Shah"), "x", PEOPLE)
    assert r.student_id == "S24011" and r.method == "roll_corrected" and r.status == "check"
    r = resolve(Claim("S2401", ""), "x", PEOPLE)  # no name to decide with
    assert r.status == "unresolved" and any(f.startswith("unknown_roll") for f in r.flags)


def test_an_unknown_roll_falls_back_to_a_single_clear_name_match():
    r = resolve(Claim("S99999", "Esha Kulkarni"), "x", PEOPLE)
    assert (r.student_id, r.method, r.status) == ("S24005", "name", "check")
    assert "matched_by_name" in r.flags and "unknown_roll:S99999" in r.flags


def test_a_misspelt_name_alone_still_finds_the_student():
    r = resolve(Claim("", "Chirag Nayar"), "x", PEOPLE)
    assert (r.student_id, r.method, r.status) == ("S24003", "name", "check")


def test_a_name_shared_by_two_students_is_not_guessed():
    r = resolve(Claim("", "Anita"), "x", PEOPLE)
    assert r.status == "unresolved" and r.student_id is None
    assert {c["student_id"] for c in r.candidates} == {"S24009", "S24010"}


def test_the_course_roster_is_preferred_when_a_name_must_be_matched():
    people = [Person("S1", "Ravi Kumar", enrolled=False), Person("S2", "Ravi Kumar", enrolled=True)]
    r = resolve(Claim("", "Ravi Kumar"), "x", people)
    assert r.student_id == "S2" and r.status == "check"  # the enrolled one, not a coin toss


def test_with_nothing_on_the_sheet_the_file_name_is_a_weak_hint():
    r = resolve(Claim(), "S24004", PEOPLE)
    assert (r.student_id, r.method, r.status) == ("S24004", "filename", "check")
    assert "from_filename" in r.flags
    assert resolve(Claim(), "IMG_0042", PEOPLE).status == "unresolved"


def test_what_the_sheet_says_beats_what_the_file_is_called():
    r = resolve(
        Claim("S24002", "Bhavna Iyer"), "S24004", PEOPLE
    )  # file says Divya, sheet says Bhavna
    assert (
        r.student_id == "S24002" and r.status == "check" and "filename_conflict:S24004" in r.flags
    )


def test_a_student_outside_the_course_is_flagged():
    r = resolve(Claim("S24012", "Late Joiner"), "x", PEOPLE)
    assert r.student_id == "S24012" and r.status == "check" and "not_enrolled" in r.flags


def test_a_second_sheet_for_the_same_student_is_held_for_a_person():
    r = resolve(Claim("S24001", "Aarav Mehta"), "again", PEOPLE, taken=["S24001"])
    assert r.status == "unresolved" and r.student_id is None and "duplicate:S24001" in r.flags


# ---------- the whole procedure, with the model ----------


def test_a_teachers_fix_overrides_everything():
    r = identify("scan.md", sheet("Name: Aarav Mehta"), PEOPLE, fixes={"scan.md": "S24004"})
    assert (r.student_id, r.method, r.status) == ("S24004", "teacher", "ok")


def test_an_unknown_fix_is_ignored():
    r = identify("scan.md", sheet("Roll No: S24001"), PEOPLE, fixes={"scan.md": "NOPE"})
    assert r.student_id == "S24001" and r.method == "roll"


def test_the_model_is_not_called_when_the_sheet_is_clear():
    client = FakeClient({})  # any call would raise KeyError
    r = identify("a.md", sheet("Name: Aarav Mehta\nRoll No: S24001"), PEOPLE, client)
    assert r.student_id == "S24001" and not client.calls


def test_the_model_copies_out_an_unlabelled_header():
    client = FakeClient({_Claimed: lambda _: {"roll_number": "S24001", "name": "Aarav Mehta"}})
    r = identify("a.md", sheet("Submitted by A. Mehta (24-001)"), PEOPLE, client)
    assert r.student_id == "S24001" and r.status == "check" and "claim_read_by_model" in r.flags
    assert client.count(_Claimed) == 1


def test_the_model_chooses_only_among_real_candidates():
    pick = {"student_id": "S24009", "reason": "The header says Anita R. in Mechanics: Rao."}
    client = FakeClient(
        {_Pick: lambda _: pick, _Claimed: lambda _: {"roll_number": "", "name": "Anita"}}
    )
    r = identify("a.md", sheet("Name: Anita"), PEOPLE, client)
    assert (r.student_id, r.method, r.status) == ("S24009", "model", "check")
    assert "model_chose" in r.flags
    seen = next(user for model, user in client.calls if model is _Pick)
    assert (
        "S24009: Anita Rao" in seen and "S24001" not in seen
    )  # only the plausible ones were shown


def test_a_model_answer_outside_the_candidates_is_rejected():
    bad = {"student_id": "S24001", "reason": "A guess."}  # a real student, but not a candidate
    client = FakeClient(
        {_Pick: lambda _: bad, _Claimed: lambda _: {"roll_number": "", "name": "Anita"}}
    )
    r = identify("a.md", sheet("Name: Anita"), PEOPLE, client)
    assert r.status == "unresolved" and r.student_id is None


def test_a_model_that_says_none_leaves_the_sheet_for_the_teacher():
    client = FakeClient(
        {_Pick: lambda _: {"student_id": "none"}, _Claimed: lambda _: {"name": "Anita"}}
    )
    r = identify("a.md", sheet("Name: Anita"), PEOPLE, client)
    assert r.status == "unresolved" and {c["student_id"] for c in r.candidates} == {
        "S24009",
        "S24010",
    }


def test_a_duplicate_is_not_sent_to_the_model_to_be_talked_into_something():
    client = FakeClient({})
    r = identify("b.md", sheet("Roll No: S24001"), PEOPLE, client, taken=["S24001"])
    assert r.status == "unresolved" and not client.calls


# ---------- the directory ----------


def make_db(path):
    con = sqlite3.connect(path)
    con.executescript(
        "CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT, email TEXT, created TEXT);"
        "CREATE TABLE enrolments (course_id INTEGER, student_id TEXT, status TEXT, at TEXT);"
        "INSERT INTO students VALUES ('S1','Asha Rao','','t'),('S2','Ben Joy','','t'),"
        "('S3','Cy Lim','','t');"
        "INSERT INTO enrolments VALUES (7,'S1','active','t'),(7,'S2','dropped','t'),"
        "(8,'S3','active','t');"
    )
    con.commit()
    con.close()


def test_the_directory_reads_the_app_database_read_only_with_course_enrolment(tmp_path):
    db = tmp_path / "app.db"
    make_db(db)
    people = {p.student_id: p for p in load_directory(db, course_id=7)}
    assert {s: p.enrolled for s, p in people.items()} == {"S1": True, "S2": False, "S3": False}
    assert people["S1"].name == "Asha Rao"
    assert all(p.enrolled for p in load_directory(db))  # no course given: nobody is excluded
    with pytest.raises(sqlite3.OperationalError):  # the connection really is read-only
        con = sqlite3.connect(db.resolve().as_uri() + "?mode=ro", uri=True)
        con.execute("DELETE FROM students")


def test_the_directory_can_be_a_roster_csv(tmp_path):
    csv = tmp_path / "roster.csv"
    csv.write_text("Student_ID,Name,Email\nS1,Asha Rao,a@x\nS2,Ben Joy,b@x\n", encoding="utf-8")
    assert [(p.student_id, p.name) for p in load_directory(csv)] == [
        ("S1", "Asha Rao"),
        ("S2", "Ben Joy"),
    ]
    bad = tmp_path / "bad.csv"
    bad.write_text("name\nX\n", encoding="utf-8")
    with pytest.raises(ValueError, match="student_id"):
        load_directory(bad)


def test_several_directories_merge_with_the_first_taking_precedence(tmp_path):
    db = tmp_path / "app.db"
    make_db(db)
    csv = tmp_path / "roster.csv"
    csv.write_text("student_id,name\nS1,Asha R.\nS9,New Joiner\nS3,\n", encoding="utf-8")
    people = {p.student_id: p for p in load_directories([db, csv], course_id=7)}
    assert people["S1"].name == "Asha Rao" and people["S1"].enrolled  # the database wins
    assert people["S9"].name == "New Joiner" and people["S9"].enrolled  # the roster adds
    assert not people["S3"].enrolled and people["S3"].name == "Cy Lim"  # not in course 7
    assert len(people) == 4


# ---------- a folder of sheets with whatever names they have ----------

PAPER = Paper(
    questions=[
        QuestionSpec(id="1", text="Explain TCP.", max_mark=4),
        QuestionSpec(id="2", text="Define BDP.", max_mark=2),
    ]
)


def test_a_folder_of_badly_named_sheets_is_attributed_by_content(tmp_path):
    files = {
        "scan_001.md": "Name: Aarav Mehta\nRoll No: S24001\n\nQ1. one\n\nQ2. two",
        "IMG_0042.txt": "Name: Bhavna Iyer\n\nQ1. uno\n\nQ2. dos",
        "final answer sheet.md": "Roll: S24O03\nName: Chirag Nair\n\nQ1. tre\n\nQ2. tres",
        "S24004.md": "Q1. no header\n\nQ2. only the file name",
        "mystery.md": "Name: Anita\n\nQ1. who\n\nQ2. knows",
        "again.md": "Roll No: S24001\n\nQ1. a second sheet\n\nQ2. same student",
        "notes.csv": "ignored,not an answer file",
    }
    for name, text in files.items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    answers, warnings, res = load_answers_identified(tmp_path, PAPER, None, PEOPLE)
    by_file = {r.source: r for r in res}
    assert set(answers) == {"S24002", "S24003", "S24004"}  # both S24001 sheets are held
    assert answers["S24003"]["2"] == "tres" and answers["S24002"]["1"] == "uno"
    assert by_file["IMG_0042.txt"].method == "name"
    assert by_file["final answer sheet.md"].method == "roll_corrected"
    assert by_file["S24004.md"].method == "filename"
    unresolved = {f for f, r in by_file.items() if r.status == "unresolved"}
    assert unresolved == {"mystery.md", "again.md", "scan_001.md"}  # two sheets, one student
    assert len(res) == 6 and "notes.csv" not in by_file
    assert all(any(f in w for w in warnings) for f in ("mystery.md", "again.md", "scan_001.md"))


def test_a_teacher_settling_one_of_two_sheets_lets_it_through(tmp_path):
    for name, body in (("a.md", "Roll No: S24001"), ("b.md", "Roll No: S24001")):
        text = f"{body}\n\nQ1. from {name}\n\nQ2. x"
        (tmp_path / name).write_text(text, encoding="utf-8")
    fixes = {"b.md": "S24001"}
    answers, _, res = load_answers_identified(tmp_path, PAPER, None, PEOPLE, fixes=fixes)
    assert answers["S24001"]["1"] == "from b.md"  # the teacher's choice stands, the other is held
    assert {r.source: r.status for r in res} == {"a.md": "unresolved", "b.md": "ok"}


def test_the_teachers_fix_brings_an_unresolved_sheet_in(tmp_path):
    (tmp_path / "mystery.md").write_text("Name: Anita\n\nQ1. who\n\nQ2. knows", encoding="utf-8")
    answers, _, res = load_answers_identified(
        tmp_path, PAPER, None, PEOPLE, fixes={"mystery.md": "S24010"}
    )
    assert set(answers) == {"S24010"} and res[0].method == "teacher"

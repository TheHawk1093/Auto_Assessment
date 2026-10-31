"""Test personas, courses, demo exams and an answer-key check, so every flow can be tried and shown.

    .venv/Scripts/python -m app.services.demo seed              # create or refresh; writes the sheet
    .venv/Scripts/python -m app.services.demo remove            # take it all away again
    .venv/Scripts/python -m app.services.demo compare <exam>    # pipeline marks against the key

Seeding creates generic accounts (admin, teacher_1, teacher_2, student_A ...), students with unique
ids (roll numbers S24001 ...), four courses across two teachers, and demo exams at different
stages. Students sit in different combinations: with teacher_1 only, with teacher_2 only, with both,
one who dropped a course, and one who was marked but never enrolled. Five exams carry fabricated
marking runs (so no model is called and nothing is spent); `[Demo] Pipeline Test` carries the real
teacher files from examples/exam_pipeline and is left ready to mark, so the pipeline can be run for
real. Seeding is repeatable: demo data is rebuilt and persona accounts keep their passwords.
Every demo account has the same simple password, `demo1234` (the admin's is `admin`): these are
made-up accounts for local trials, not real users, so change them before exposing the app on a
network. The accounts are listed, with each
persona's story and what to try, to app_data/demo_personas.md (git-ignored). Demo exam ids start
with `demo-`; `remove` deletes exactly the demo exams, courses, students and persona accounts.
"""

from __future__ import annotations

import csv
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path
from typing import NamedTuple

from app import config
from app.services import auth, courses, db, publishing, regrades, results, storage
from app.services.demo_pdf import pdf_bytes
from autograde.schemas import Feedback, Grading, Improvement, Item, PointVerdict, Result

PREFIX = "demo-"
PIPELINE_DIR = config.ROOT / "examples" / "exam_pipeline"
EXPECTED = PIPELINE_DIR / "expected_marks.csv"
# Accounts earlier versions of the seeder created under first names; replaced, not kept.
LEGACY = ("admin_demo", "teacher_rao", "teacher_iyer", "alice", "bob", "cara", "dev", "esha")

# Unique student ids (roll numbers). A login username is separate: student_A signs in as S24001.
A, B, C, D, E, F, G, H = (f"S24{n:03d}" for n in range(1, 9))
ROLLS = (A, B, C, D, E, F, G, H)
NAMES = dict(
    zip(
        ROLLS,
        (
            "Aarav Mehta", "Bhavna Iyer", "Chirag Nair", "Divya Menon",
            "Esha Kulkarni", "Farhan Qureshi", "Gauri Deshmukh", "Harish Pillai",
        ),
        strict=True,
    )
)  # fmt: skip
TEACHERS = ("teacher_1", "teacher_2")


@dataclass(frozen=True)
class Persona:
    """A demo account: who it is, the story it tells and what to try with it."""

    username: str
    role: str
    name: str
    title: str
    story: str
    try_this: tuple[str, ...]
    password: str = "demo1234"  # the shared dummy password (see DEMO_PASSWORD)
    student_id: str = ""  # students only


PERSONAS = [
    Persona(
        "admin",
        "admin",
        "Administrator",
        "The administrator",
        "Runs the system: accounts, which AI models teachers may use, courses and students, and "
        "what is running. Password is `admin`: for local demos only; change it before exposing the "
        "app on a network.",
        (
            "Admin, Users: add a teacher, reset a password, disable an account.",
            "Admin, Courses and students: every course with its teacher and head-count, and every "
            "student with the courses they are in.",
            "Admin, AI models: switch a model off and see it vanish from a teacher's Settings. "
            "Switch a model off and it disappears from a teacher's Settings.",
        ),
        password="admin",
    ),
    Persona(
        "teacher_1",
        "teacher",
        "Teacher 1",
        "Teaches three courses",
        "Runs ME1001 Engineering Mechanics, ME1002 Thermodynamics and ME1003 Strength of Materials "
        "(the last has the real Pipeline Test, ready to mark, and nobody enrolled yet).",
        (
            "Home, Courses tab: three courses with their rosters; enrol or remove a student.",
            "Pipeline Test: Mark tab, Prepare, then Mark all answers (examples/exam_pipeline/README.md); "
            "then Publish, 'Enrol students and create missing accounts'.",
            "Mechanics Quiz, Publish tab: S24007 was marked but is not enrolled, so cannot see the result.",
            "Mechanics Quiz, Regrades tab: decide student_A's pending request, then sign in as student_A.",
            "Thermodynamics Midterm is marked but unpublished: publish it and watch student_A, B and C "
            "get a second exam on their grade cards.",
        ),
    ),
    Persona(
        "teacher_2",
        "teacher",
        "Teacher 2",
        "Teaches Circuits, and shares a student with teacher_1",
        "Runs EE1001 Circuits. Cannot see teacher_1's exams or courses. student_A is enrolled with "
        "both teachers; student_D with this teacher only.",
        (
            "Home: only the two Circuits exams, only the Circuits course.",
            "Circuits Lab Test is marked but unpublished: publish it and watch student_A and student_D's "
            "grade cards change.",
            "Change a mark in the Circuits Quiz and sign in as student_A: the EE1001 percentage moves, "
            "the ME1001 one does not.",
        ),
    ),
    Persona(
        "student_A",
        "student",
        NAMES[A],
        "Enrolled with both teachers (S24001)",
        "In ME1001 and ME1002 under teacher_1 and EE1001 under teacher_2. Scored 9 of 10 on the "
        "Mechanics Quiz and has one regrade request waiting. The grade card shows both teachers.",
        (
            "My results, Grade card: ME1001 (teacher_1) and EE1001 (teacher_2), each with its own percentage.",
            "Exam details: the pending request; one request is left, submit a second and see the limit hold.",
        ),
        student_id=A,
    ),
    Persona(
        "student_B",
        "student",
        NAMES[B],
        "Teacher 1 only; a regrade was upheld (S24002)",
        "Teacher 1 raised question 2 from 1 to 2 after a request. The Mechanics total and the question "
        "show 'Changed by your teacher' with the note. No Circuits course.",
        ("Grade card: only teacher_1's courses. Exam details: the changed mark and the reply.",),
        student_id=B,
    ),
    Persona(
        "student_C",
        "student",
        NAMES[C],
        "Teacher 1 only; struggling (S24003)",
        "Low marks and plenty of feedback to read; the full regrade allowance is unused.",
        (
            "Exam details: lots of feedback, mostly red and amber bars.",
            "Try a too-short reason (rejected), then a proper one (accepted).",
        ),
        student_id=C,
    ),
    Persona(
        "student_D",
        "student",
        NAMES[D],
        "Teacher 2 only (S24004)",
        "Enrolled only in EE1001 under teacher_2: the grade card shows that one course and nothing from "
        "teacher_1. The Circuits Lab Test is marked but unpublished.",
        (
            "Grade card: one course. Ask teacher_2 to publish the Lab Test, refresh, and the course "
            "percentage changes.",
        ),
        student_id=D,
    ),
    Persona(
        "student_E",
        "student",
        NAMES[E],
        "Hindi answers with maths (S24005)",
        "Wrote the Mechanics Quiz in Hindi with formulas. Checks Devanagari text and KaTeX rendering.",
        (
            "Exam details and the teacher's Results tab: the Hindi answers and the formulas render "
            "properly. (If you see boxes, install Noto Sans Devanagari.)",
        ),
        student_id=E,
    ),
    Persona(
        "student_F",
        "student",
        NAMES[F],
        "Dropped a course after the exam (S24006)",
        "Was marked in the Mechanics Quiz, then dropped ME1001. The marks are kept but the course is "
        "gone from the grade card and the exam from the list.",
        (
            "Grade card: empty. As teacher_1, Courses tab, re-enrol S24006 in ME1001: the course and the "
            "marks come back on the next refresh.",
        ),
        student_id=F,
    ),
    Persona(
        "student_G",
        "student",
        NAMES[G],
        "Marked but never enrolled (S24007)",
        "Has an answer in the Mechanics Quiz but was never enrolled in ME1001, a data mismatch the "
        "system must not paper over.",
        (
            "Grade card: empty, and the Mechanics Quiz is refused. As teacher_1, Publish tab: a warning "
            "names S24007; enrol them and the result appears.",
        ),
        student_id=G,
    ),
]


# ---------- the courses, enrolments and exams ----------


@dataclass
class DemoExam:
    """A fabricated exam for the demo: its questions and each student's marked answers."""

    key: str
    title: str
    course: str  # key in COURSES
    stage: str  # draft | ready | marked | published
    questions: list[dict] = field(default_factory=list)
    answers: dict = field(default_factory=dict)  # roll number -> {qid: (answer, mark, flags)}


# key -> (code, title, term, teacher)
COURSES = {
    "mech": ("ME1001", "Engineering Mechanics", "2026 Autumn", "teacher_1"),
    "thermo": ("ME1002", "Thermodynamics", "2026 Autumn", "teacher_1"),
    "som": ("ME1003", "Strength of Materials", "2026 Autumn", "teacher_1"),
    "circuits": ("EE1001", "Circuits", "2026 Autumn", "teacher_2"),
}
# course key -> enrolled roll numbers. Beyond these: F was enrolled in mech and dropped; G never was.
ENROLMENTS = {
    "mech": [A, B, C, E],
    "thermo": [A, B, C],
    "circuits": [A, D],
    "som": [],  # the pipeline demo starts with an empty roster: enrolling is part of the demo
}

MECH_Q = [
    {"id": "1", "max_mark": 4.0, "kind": "maths",
     "text": r"Derive the range of a projectile launched at speed $u$ and angle $\theta$ on level ground."},
    {"id": "2", "max_mark": 3.0, "kind": "numeric",
     "text": r"A 2 kg block slides down a frictionless incline of $30^\circ$. Find its acceleration ($g = 9.8\ \mathrm{m/s^2}$)."},
    {"id": "3", "max_mark": 3.0, "kind": "short",
     "text": "State Newton's second law and give one example."},
]  # fmt: skip
MODEL = {
    ("mech", "1"): r"Time of flight $T = 2u\sin\theta/g$; range $R = u\cos\theta \cdot T = u^2\sin 2\theta / g$.",
    ("mech", "2"): r"$a = g\sin\theta = 9.8 \times 0.5 = 4.9\ \mathrm{m/s^2}$ down the slope.",
    ("mech", "3"): "The net force on a body equals its mass times its acceleration, $F = ma$. Example: pushing a trolley.",
}  # fmt: skip
MECH_ANSWERS = {
    A: {
        "1": (r"Time of flight $T = 2u\sin\theta/g$. Range $R = u\cos\theta\,T = \frac{u^2\sin 2\theta}{g}$.", 4.0, []),
        "2": (r"Along the slope $ma = mg\sin 30^\circ$, so $a = g\sin 30^\circ = 9.8 \times 0.5 = 4.9$ m/s^2.", 2.0, ["models_disagree"]),
        "3": ("Net force equals mass times acceleration, F = ma. Example: a harder push makes a trolley speed up faster.", 3.0, []),
    },
    B: {
        "1": (r"Horizontal speed is $u\cos\theta$ and the time in the air is $2u\sin\theta/g$, so the range is $u^2\sin 2\theta/g$ roughly.", 3.0, []),
        "2": ("The block speeds up because of gravity along the slope, a = g sin 30.", 1.0, []),
        "3": ("Force is mass times acceleration.", 2.0, []),
    },
    C: {
        "1": ("The ball goes up and comes down so the range is how far it goes.", 1.0, ["retried"]),
        "2": ("I think the acceleration is 9.8 because of gravity.", 0.0, []),
        "3": ("Newton said force depends on mass and acceleration.", 1.5, []),
    },
    E: {
        "1": (r"The time of flight is $T = 2u\sin\theta/g$, so the range is $R = u\cos\theta \cdot T = \frac{u^2 \sin 2\theta}{g}$.", 3.0, []),
        "2": (r"Along the slope $a = g\sin 30^\circ = 4.9\,\mathrm{m/s^2}$.", 3.0, []),
        "3": (r"Newton's second law: force $F = ma$, the product of mass and acceleration.", 2.0, []),
    },
    F: {  # dropped the course afterwards: the marks stay
        "1": (r"Range is $R = u^2\sin 2\theta/g$ from the time of flight $2u\sin\theta/g$.", 3.5, []),
        "2": ("a = g sin 30 = 4.9 m/s^2", 3.0, []),
        "3": ("Force equals mass times acceleration, for example a pushed trolley.", 3.0, []),
    },
    G: {  # marked but never enrolled
        "1": ("Range depends on speed and angle.", 1.5, []),
        "2": ("About 5 m/s^2 down the slope.", 1.5, []),
        "3": ("F = ma.", 2.0, []),
    },
}  # fmt: skip

THERMO_Q = [
    {"id": "1", "max_mark": 3.0, "kind": "short", "text": "State the first law of thermodynamics."},
    {"id": "2", "max_mark": 4.0, "kind": "maths",
     "text": r"One mole of an ideal gas expands isothermally at $T$ from $V_1$ to $V_2$. Find the work done by the gas."},
]  # fmt: skip
THERMO_ANSWERS = {
    A: {"1": ("Energy is conserved: $\\Delta U = Q - W$.", 3.0, []),
        "2": (r"$W = RT\ln(V_2/V_1)$", 4.0, [])},
    B: {"1": ("Heat added equals work done plus change in internal energy.", 3.0, []),
        "2": (r"$W = P\Delta V$ so $W = P(V_2 - V_1)$", 1.0, [])},
    C: {"1": ("Energy cannot be created.", 1.5, []),
        "2": ("I do not remember the formula.", 0.0, [])},
}  # fmt: skip

CIRCUIT_Q = [
    {"id": "1", "max_mark": 3.0, "kind": "short", "text": "State Kirchhoff's voltage law."},
    {"id": "2", "max_mark": 3.0, "kind": "numeric",
     "text": r"Find the equivalent resistance of $6\ \Omega$ and $3\ \Omega$ in parallel."},
]  # fmt: skip
CIRCUIT_ANSWERS = {
    D: {"1": ("The sum of voltages around any closed loop is zero.", 3.0, []),
        "2": (r"$R = \frac{6\times 3}{6+3} = 2\ \Omega$", 3.0, [])},
    A: {"1": ("Voltages in a loop add up to zero.", 3.0, []),
        "2": (r"$R = 6 + 3 = 9\ \Omega$", 0.0, [])},
}  # fmt: skip

LAB_Q = [
    {"id": "1", "max_mark": 4.0, "kind": "short", "text": "State Ohm's law and one condition for it to hold."},
    {"id": "2", "max_mark": 4.0, "kind": "numeric",
     "text": r"A 12 V battery drives a current through $4\ \Omega$ and $2\ \Omega$ in series. Find the current."},
]  # fmt: skip
LAB_ANSWERS = {
    D: {"1": ("Voltage is proportional to current at constant temperature, V = IR.", 4.0, []),
        "2": (r"$I = 12/(4+2) = 2\ \mathrm{A}$", 4.0, [])},
    A: {"1": ("V = IR.", 2.0, []),
        "2": (r"$I = 12/4 = 3\ \mathrm{A}$", 0.0, [])},
}  # fmt: skip

# Written by hand for every answer that lost marks: (exam, student, question) -> a `Note`'s
# fields in order (see `Note` below).
# Quotes are words the student wrote; a point with no marks has an empty quote.
FEEDBACK = {
    ("mech", A, "2"): (
        "so $a = g\\sin 30^\\circ = 9.8 \\times 0.5 = 4.9$", "Method and value are correct.",
        "", "The direction of the acceleration is not stated.",
        "You used the component of gravity along the slope and got 4.9.",
        "The direction of the acceleration is not stated.",
        "The question asks for the acceleration, which is a vector.",
        "Add that it is directed down the slope.", "partial",
    ),
    ("mech", B, "1"): (
        "the time in the air is $2u\\sin\\theta/g$", "Horizontal speed and time in the air are both given.",
        "so the range is $u^2\\sin 2\\theta/g$ roughly", "The result is right but 'roughly' hides the missing step.",
        "You found both the horizontal speed and the time in the air.",
        "The step from the product to $u^2\\sin 2\\theta/g$ is not shown.",
        "Without it the formula looks guessed rather than derived.",
        "Multiply $u\\cos\\theta$ by $2u\\sin\\theta/g$ and use $2\\sin\\theta\\cos\\theta=\\sin 2\\theta$.",
        "partial",
    ),
    ("mech", B, "2"): (
        "a = g sin 30", "The right component of gravity is chosen.",
        "", "The number is never worked out.",
        "You chose the component of gravity along the slope.",
        "The numerical value of the acceleration is missing.",
        "The question asks for a value, not only the formula.",
        "Substitute $\\sin 30^\\circ = 0.5$ to get $4.9\\ \\mathrm{m/s^2}$.", "partial",
    ),
    ("mech", B, "3"): (
        "Force is mass times acceleration.", "The law is stated correctly.",
        "", "No example is given.",
        "You stated the law correctly.", "No example is given.",
        "An example shows you can apply the law, not only recite it.",
        "Add one, such as a harder push making a trolley speed up faster.", "partial",
    ),
    ("mech", C, "1"): (
        "The ball goes up and comes down", "The motion is described, but only in words.",
        "", "No formula or derivation of the range.",
        "You describe the ball going up and coming down.",
        "The range is not derived.",
        "Range is horizontal speed multiplied by the time in the air.",
        "Find $T = 2u\\sin\\theta/g$ first, then multiply by $u\\cos\\theta$.", "incorrect",
    ),
    ("mech", C, "2"): (
        "", "No method for the incline.",
        "", "The value 9.8 ignores the slope.",
        "You attempted the question.",
        "The acceleration is taken as $g$, not the part of gravity along the slope.",
        "On a frictionless incline only the component along the slope accelerates the block.",
        "Use $a = g\\sin 30^\\circ = 4.9\\ \\mathrm{m/s^2}$.", "incorrect",
    ),
    ("mech", C, "3"): (
        "force depends on mass and acceleration", "Both quantities are named.",
        "", "No formula and no example.",
        "You named mass and acceleration as what the force depends on.",
        "The law is not written as $F = ma$ and no example is given.",
        "The exact relation is what makes it a law.",
        "State $F = ma$ and add an example such as a pushed trolley.", "partial",
    ),
    ("mech", E, "1"): (
        "so the range is $R = u\\cos\\theta \\cdot T", "The range is built from the time of flight.",
        "", "The simplification to $u^2\\sin 2\\theta/g$ skips a step.",
        "You derived the range from the time of flight.",
        "The step from $2u^2\\sin\\theta\\cos\\theta/g$ to $u^2\\sin 2\\theta/g$ is not shown.",
        "The identity is what turns the product into the standard formula.",
        "Add the double-angle identity $2\\sin\\theta\\cos\\theta=\\sin 2\\theta$.", "partial",
    ),
    ("mech", E, "3"): (
        "force $F = ma$", "The law is stated correctly.",
        "", "No example is given.",
        "You stated the law as $F = ma$.", "No example is given.",
        "An example shows you can apply the law, not only recite it.",
        "Add one, such as a pushed trolley accelerating more when the push is larger.", "partial",
    ),
    ("mech", F, "1"): (
        "from the time of flight $2u\\sin\\theta/g$", "The time of flight is used.",
        "", "The horizontal speed $u\\cos\\theta$ is not mentioned.",
        "You gave the correct range formula and the time of flight.",
        "The horizontal speed is not mentioned.",
        "The range is the horizontal speed multiplied by the time in the air.",
        "Say that the range is $u\\cos\\theta \\times T$.", "partial",
    ),
    ("mech", G, "1"): (
        "Range depends on speed and angle.", "The two quantities are named.",
        "", "No formula or derivation.",
        "You named speed and angle as what the range depends on.",
        "There is no formula for the range.",
        "The question asks you to derive it.",
        "Find $T = 2u\\sin\\theta/g$, then multiply by $u\\cos\\theta$.", "partial",
    ),
    ("mech", G, "2"): (
        "down the slope", "The direction is right and the value is close.",
        "", "No working shows where about 5 comes from.",
        "You gave the right direction and a close value.",
        "The value is rounded and there is no working.",
        "The exact value follows from one line of working.",
        "Show $a = g\\sin 30^\\circ = 4.9\\ \\mathrm{m/s^2}$.", "partial",
    ),
    ("mech", G, "3"): (
        "F = ma", "The law is written correctly.",
        "", "No explanation and no example.",
        "You wrote the law correctly.", "No explanation or example is given.",
        "A sentence and an example show you understand what the symbols mean.",
        "Say what $F$, $m$ and $a$ are and add an example.", "partial",
    ),
    ("thermo", B, "2"): (
        "$W = P\\Delta V$", "Work done by the gas is the starting point.",
        "", "Pressure is not constant in an isothermal expansion.",
        "You started from the work done by the gas.",
        "$W = P\\Delta V$ assumes constant pressure.",
        "In an isothermal expansion the pressure falls as the volume grows.",
        "Use $P = RT/V$ and integrate: $W = RT\\ln(V_2/V_1)$.", "incorrect",
    ),
    ("thermo", C, "1"): (
        "Energy cannot be created.", "Conservation of energy is the core idea.",
        "", "Heat, work and internal energy are not linked.",
        "You state that energy is conserved.",
        "The link between heat, work and internal energy is missing.",
        "The first law says how these three quantities are related.",
        "Write $\\Delta U = Q - W$ and say what each symbol stands for.", "partial",
    ),
    ("thermo", C, "2"): (
        "", "No attempt at the integral.",
        "", "No answer is given.",
        "You attempted the question.",
        "No expression for the work is given.",
        "Even a start earns marks.",
        "Start from $W = \\int P\\,dV$ with $P = RT/V$.", "incorrect",
    ),
    ("circuits", A, "2"): (
        "$R = 6 + 3 = 9\\ \\Omega$", "Both resistor values are used.",
        "", "The resistors are added as if they were in series.",
        "You used both resistor values.",
        "The resistors are added as if they were in series.",
        "In parallel the total is smaller than either resistor.",
        "Use $R = \\frac{6\\times 3}{6+3} = 2\\ \\Omega$.", "incorrect",
    ),
    ("lab", A, "1"): (
        "V = IR", "The relation is written correctly.",
        "", "No condition for the law to hold is given.",
        "You wrote the relation $V = IR$.",
        "No condition for the law to hold is given.",
        "Ohm's law only holds when conditions such as temperature stay constant.",
        "Add that the temperature must stay constant.", "partial",
    ),
    ("lab", A, "2"): (
        "", "No method for finding the total resistance.",
        "", "One of the two resistors is left out.",
        "You used Ohm's law to find the current.",
        "Only the $4\\ \\Omega$ resistor is used.",
        "In series the resistances add before you divide the voltage by them.",
        "Use $I = 12/(4+2) = 2\\ \\mathrm{A}$.", "incorrect",
    ),
}


class Note(NamedTuple):
    """The marker's reasons for one answer that lost marks, point by point."""

    point1_quote: str  # words the student wrote that earned (or failed to earn) point 1
    point1_reason: str
    point2_quote: str  # empty when the point earned nothing
    point2_reason: str
    strength: str  # one thing the answer did well
    issue: str  # what cost the marks
    why: str  # why it matters
    fix: str  # what to write next time
    kind: str  # partial | incorrect


def item_key(exam_key: str, student: str, question: str) -> str:
    """The id of one answer, `<exam id>/<student id>/<question id>`: the same as `Item.id`."""
    return f"{PREFIX}{exam_key}/{student}/{question}"


# Notes by answer id. An answer is matched to its note by exam, student and question together, so
# one exam's feedback can never be shown on another's.
NOTES: dict[str, Note] = {item_key(*key): Note(*note) for key, note in FEEDBACK.items()}


def check_notes(ex: DemoExam) -> None:
    """Fail loudly when an exam's feedback does not fit its answers.

    Every answer below full marks needs a note, no note may sit on a full-marks answer or on an
    answer that does not exist, and each quote must be words from that student's answer.
    """
    wanted = set()
    for student, per_q in ex.answers.items():
        for q in ex.questions:
            answer, mark, _ = per_q[q["id"]]
            key = item_key(ex.key, student, q["id"])
            note = NOTES.get(key)
            if mark >= q["max_mark"]:
                if note:
                    raise ValueError(f"{key}: full marks but has feedback")
                continue
            wanted.add(key)
            if note is None:
                raise ValueError(f"{key}: lost marks but has no feedback")
            for quote in (note.point1_quote, note.point2_quote):
                if quote and quote not in answer:
                    raise ValueError(f"{key}: quote {quote!r} is not in the student's answer")
    own = f"{PREFIX}{ex.key}/"
    if stray := [k for k in NOTES if k.startswith(own) and k not in wanted]:
        raise ValueError(f"feedback for answers that do not exist or have full marks: {stray}")


EXAMS = [
    DemoExam("mech", "[Demo] Mechanics Quiz", "mech", "published", MECH_Q, MECH_ANSWERS),
    DemoExam("thermo", "[Demo] Thermodynamics Midterm", "thermo", "marked", THERMO_Q, THERMO_ANSWERS),
    DemoExam("fluids", "[Demo] Fluids Test", "thermo", "draft"),
    DemoExam("pipeline", "[Demo] Pipeline Test (ready to mark)", "som", "ready"),
    DemoExam("messy", "[Demo] Messy Scans (who wrote what?)", "som", "ready"),
    DemoExam("circuits", "[Demo] Circuits Quiz", "circuits", "published", CIRCUIT_Q, CIRCUIT_ANSWERS),
    DemoExam("lab", "[Demo] Circuits Lab Test", "circuits", "marked", LAB_Q, LAB_ANSWERS),
]  # fmt: skip


def exam_id(key: str) -> str:
    """Return the app exam id used for a demo exam key."""
    return f"{PREFIX}{key}"


def _result(
    ex: DemoExam, student: str, q: dict, answer: str, mark: float, flags: list[str]
) -> Result:
    """One fabricated marked answer: two points worth half the question each, and feedback."""
    qid, top = q["id"], q["max_mark"]
    half = top / 2
    got = [min(mark, half), max(mark - half, 0.0)]
    note = NOTES.get(item_key(ex.key, student, qid))
    verdicts = []
    for i, a in enumerate(got, 1):
        status = "met" if a >= half else "partial" if a > 0 else "not_met"
        if note:
            evidence = (note.point1_quote, note.point2_quote)[i - 1]
            reason = (note.point1_reason, note.point2_reason)[i - 1]
        else:
            evidence, reason = "", "Matches the model answer."
        if a > 0 and not evidence:
            evidence = answer[:80]
        verdicts.append(
            PointVerdict(
                point_id=f"p{i}", status=status, marks_awarded=a, evidence=evidence, reason=reason
            )
        )
    feedback = None
    if note:
        lost = "p1" if got[0] < half else "p2"
        feedback = Feedback(
            strengths=[note.strength],
            improvements=[
                Improvement(
                    point_id=lost, kind=note.kind, issue=note.issue, why=note.why, fix=note.fix
                )
            ],
            summary=f"Next time: {note.fix}",
        )
    item = Item(
        id=f"{exam_id(ex.key)}/{student}/{qid}", dataset="exam", question_id=qid,
        question=q["text"], model_answer=MODEL.get((ex.key, qid), "See the marking scheme."),
        student_answer=answer, max_mark=top, kind=q["kind"],
    )  # fmt: skip
    return Result(
        item=item, mode="pipeline", predicted_mark=mark,
        grading=Grading(verdicts=verdicts), feedback=feedback, flags=flags,
    )  # fmt: skip


def _write_run(ex: DemoExam) -> None:
    check_notes(ex)
    eid = exam_id(ex.key)
    run = storage.run_path(eid)
    (run / "students").mkdir(parents=True, exist_ok=True)
    students = list(ex.answers)
    intake = {
        "paper": {"questions": ex.questions},
        "students": students,
        "rules": {},
        "warnings": [],
    }
    (run / "intake.json").write_text(json.dumps(intake), encoding="utf-8")
    header = ["student", *[q["id"] for q in ex.questions], "total"]
    rows = [",".join(header)]
    lines = []
    for student, per_q in ex.answers.items():
        marks = [per_q[q["id"]][1] for q in ex.questions]
        rows.append(",".join([student, *(f"{m:g}" for m in marks), f"{sum(marks):g}"]))
        for q in ex.questions:
            answer, mark, flags = per_q[q["id"]]
            lines.append(_result(ex, student, q, answer, mark, flags).model_dump_json())
    (run / "marks.csv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    (run / "results.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
    schemes = [
        f"## Question {q['id']} ({q['max_mark']:g} marks)\n\n{q['text']}\n" for q in ex.questions
    ]
    (run / "schemes.md").write_text("\n".join(schemes), encoding="utf-8")


def _write_uploads(ex: DemoExam, pdf: bool = False) -> None:
    """The files a teacher would have uploaded for a fabricated exam, so the Upload tab is full.

    With `pdf` the paper and the model answers are PDF files, as teachers often have them.
    """
    eid = exam_id(ex.key)
    paper = "\n\n".join(f"{q['id']}. [{q['max_mark']:g} marks] {q['text']}" for q in ex.questions)
    refs = "\n\n".join(
        f"{q['id']}. {MODEL.get((ex.key, q['id']), 'Marks for the key ideas.')}"
        for q in ex.questions
    )
    paper_text = f"# {ex.title}\n\n{paper}\n"
    if pdf:
        files = [("paper.pdf", pdf_bytes(paper_text))]
        ref_files = [("model_answer.pdf", pdf_bytes(refs))]
    else:
        files = [("paper.md", paper_text.encode())]
        ref_files = [("model_answer.md", refs.encode())]
    storage.save_uploads(eid, "paper", files, False, set())
    storage.save_uploads(eid, "reference", ref_files, False, set())
    files = []
    for student, per_q in ex.answers.items():
        body = "\n\n".join(f"{qid}. {answer}" for qid, (answer, _, _) in per_q.items())
        files.append((f"{student}.md", body.encode()))
    storage.save_uploads(eid, "answers", files, False, set())


def _write_pipeline_uploads(ex: DemoExam) -> None:
    """Upload the real files from examples/exam_pipeline, as a teacher would.

    The exam is left ready to mark. The messy exam uses the same paper and rubric with sheets that
    have arbitrary file names and imperfect headers, so the pipeline has to work out who wrote
    each from the sheet itself.
    """
    eid = exam_id(ex.key)
    folder = "answers_messy" if ex.key == "messy" else "answers"

    def read(*names: str) -> list[tuple[str, bytes]]:
        return [(n, (PIPELINE_DIR / n).read_bytes()) for n in names]

    storage.save_uploads(eid, "paper", read("paper.md"), False, set())
    storage.save_uploads(eid, "reference", read("model_answer.md", "rubric.md"), False, set())
    answers = [
        (p.name, p.read_bytes()) for p in sorted((PIPELINE_DIR / folder).glob("*.md"))
    ] + read("roster.csv")
    storage.save_uploads(eid, "answers", answers, False, {".csv"})
    if ex.key == "pipeline":
        storage.update_settings(eid, struck_out=[f"{F}=6"])


# ---------- seeding ----------


def _known_passwords(app_data: Path) -> dict[str, str]:
    """Passwords the last seed wrote, so personas that already exist keep theirs."""
    sheet = app_data / "demo_personas.md"  # rows look like: | `user` | role | `password` |
    if not sheet.exists():
        return {}
    rows = re.findall(r"^\| `([^`]+)` \| \w+ \| `([^`]+)` \|$", sheet.read_text("utf-8"), re.M)
    return dict(rows)


CASE_EXAMS = tuple(f"case{n}-demo" for n in range(1, 5))  # made by app/services/cases.py


def forget_exam(eid: str) -> None:
    """Delete an exam's files and every record about it: overrides, regrades, hand-ins, messages."""
    storage.delete_exam(eid)
    with db.connect() as c:
        for table in ("overrides", "regrades", "submissions", "notifications"):
            c.execute(f"DELETE FROM {table} WHERE exam_id = ?", (eid,))


_forget_exam = forget_exam


def _forget_people() -> None:
    """Remove the demo courses, enrolments, students and accounts (and the older first-name ones)."""
    names = [p.username for p in PERSONAS] + list(LEGACY)
    marks = ",".join("?" * len(TEACHERS))
    with db.connect() as c:
        ids = [
            r[0] for r in c.execute(f"SELECT id FROM courses WHERE teacher IN ({marks})", TEACHERS)
        ]
        for cid in ids:
            c.execute("DELETE FROM enrolments WHERE course_id = ?", (cid,))
        c.execute(f"DELETE FROM courses WHERE teacher IN ({marks})", TEACHERS)
        c.execute(
            f"DELETE FROM enrolments WHERE student_id IN ({','.join('?' * len(ROLLS))})", ROLLS
        )
        links = [r[0] for r in c.execute(
            f"SELECT student_id FROM users WHERE username IN ({','.join('?' * len(names))}) "
            "AND student_id IS NOT NULL", names)]  # fmt: skip
        c.execute(f"DELETE FROM users WHERE username IN ({','.join('?' * len(names))})", names)
        gone = [*ROLLS, *links]
        c.execute(
            f"DELETE FROM submissions WHERE student_id IN ({','.join('?' * len(gone))})", gone
        )
        c.execute(f"DELETE FROM students WHERE student_id IN ({','.join('?' * len(gone))})", gone)


def seed(app_data: Path = config.APP_DATA) -> dict[str, str]:
    """Create the personas, courses, enrolments and exams. Returns {username: password}."""
    known = _known_passwords(app_data)
    for ex in EXAMS:
        _forget_exam(exam_id(ex.key))
    _forget_people()
    (app_data / "demo_accounts.csv").unlink(missing_ok=True)
    passwords = {}
    for p in PERSONAS:
        wanted = p.password or known.get(p.username) or auth.generate_password(12)
        auth.create_user(
            p.username, p.role, p.name, wanted, by="demo", allow_short=True,
            student_id=p.student_id or None,
        )  # fmt: skip
        passwords[p.username] = wanted
    ids = {}
    for key, (code, title, term, teacher) in COURSES.items():
        ids[key] = courses.create_course(code, title, teacher, term, by="demo")
        for roll in ENROLMENTS[key]:
            courses.enrol(ids[key], roll, "demo")
    courses.enrol(ids["mech"], F, "demo")  # F was enrolled in Mechanics...
    courses.drop(ids["mech"], F, "demo")  # ...and dropped it after the exam; G never was
    for ex in EXAMS:
        eid = exam_id(ex.key)
        owner = COURSES[ex.course][3]
        storage.create_exam(ex.title, owner=owner, exam_id=eid, course_id=ids[ex.course])
        if ex.stage == "ready":
            _write_pipeline_uploads(ex)
        elif ex.stage != "draft":
            _write_uploads(ex)
            _write_run(ex)
    _scenario_publish_and_regrades()
    _write_sheet(passwords, app_data / "demo_personas.md")
    return passwords


def _scenario_publish_and_regrades() -> None:
    """Publish two demo exams and file regrade requests on one.

    Mechanics (teacher_1) and the Circuits Quiz (teacher_2) are published; A's request waits and
    B's was upheld. The Thermodynamics Midterm and the Circuits Lab Test stay unpublished.
    """
    mech, circuits = exam_id("mech"), exam_id("circuits")
    publishing.publish(mech, by="teacher_1")
    publishing.publish(circuits, by="teacher_2")
    regrades.submit(
        mech, A, "2", "missed_point",
        "I wrote a = g sin 30 = 9.8 x 0.5 = 4.9 m/s^2 with the working shown, so the numerical "
        "answer and the method should both be credited in full.",
    )  # fmt: skip
    other = regrades.submit(
        mech, B, "2", "unfair_deduction",
        "I used the component of gravity along the slope, which is the right method, "
        "so I should get credit for the method even without the number.",
    )  # fmt: skip
    regrades.decide(
        other, upheld=True, by="teacher_1", new_mark=2.0,
        reply="You are right: the method earns a second mark. The number was still missing, so not full marks.",
    )  # fmt: skip


def _write_sheet(passwords: dict[str, str], path: Path) -> None:
    lines = [
        "# Test personas",
        "",
        "Sign in at the app's login page. Every account uses the dummy password `demo1234` except the admin (`admin`). This file is git-ignored.",
        "Rebuild the scenario any time with `python -m app.services.demo seed`; remove it all with `remove`.",
        "",
        "| Username | Role | Password |",  # the seeder reads these rows back to keep passwords
        "|---|---|---|",
    ]
    lines += [f"| `{p.username}` | {p.role} | `{passwords[p.username]}` |" for p in PERSONAS]
    lines += ["", "Student ids (roll numbers, unique) and names:", ""]
    lines += [f"- `{p.username}` = {p.student_id}, {p.name}" for p in PERSONAS if p.student_id]
    lines.append(f"- (no account yet) = {H}, {NAMES[H]}")
    lines += ["", "## Who is in which course", ""]
    for key, (code, title, _, teacher) in COURSES.items():
        who = ", ".join(ENROLMENTS[key]) or "nobody yet"
        lines.append(f"- **{code} {title}** ({teacher}): {who}")
    lines.append(
        f"- Dropped: {F} left ME1001 after the exam. Never enrolled: {G} (marked in ME1001 anyway)."
    )
    lines += ["", "## Exams", ""]
    lines += [f"- **{ex.title}** ({COURSES[ex.course][0]}, {ex.stage})" for ex in EXAMS]
    lines += [
        "",
        "`[Demo] Pipeline Test` holds the real files from `examples/exam_pipeline/` (8 students, 6 questions);",
        "its README lists what each student is designed to show and the expected marks. It starts with nobody",
        "enrolled: after marking, 'Enrol students and create missing accounts' on the Publish tab does it.",
        "",
        "`[Demo] Messy Scans` holds the same answers in `examples/exam_pipeline/answers_messy/`: arbitrary file",
        "names, a roll number with a letter O for a zero, a name with no roll number, a sheet with no header,",
        "a roll number and name that disagree, a sheet with nothing usable, and two sheets for one student.",
        "Prepare it and read 'Who wrote which sheet' on the Mark tab: the pipeline matches each sheet to the",
        "student database by roll number first and name second, and asks you only about what it cannot settle.",
    ]
    for p in PERSONAS:
        lines += ["", f"## {p.name} (`{p.username}`): {p.title}", "", p.story, "", "Try:"]
        lines += [f"- {t}" for t in p.try_this]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def remove(app_data: Path = config.APP_DATA) -> None:
    """Delete the demo exams, courses, students and persona accounts (and nothing else)."""
    for ex in EXAMS:
        forget_exam(exam_id(ex.key))
    for eid in CASE_EXAMS:
        forget_exam(eid)
    _forget_people()
    for name in ("demo_personas.md", "demo_accounts.csv"):
        (app_data / name).unlink(missing_ok=True)


# ---------- the answer key ----------


def _norm_q(qid: str) -> str:
    return re.sub(r"[^a-z0-9]", "", qid.lower().removeprefix("q"))


def load_expected(path: Path = EXPECTED) -> dict[tuple[str, str], float | None]:
    """{(student id, question): the person's mark}; None where the question was not to be marked."""
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    out = {}
    for row in rows:
        for q, value in row.items():
            if q != "student":
                out[(row["student"], _norm_q(q))] = float(value) if value.strip() else None
    return out


def compare(exam: str, path: Path = EXPECTED, tolerance: float = 1.0) -> list[dict]:
    """Compare the pipeline's marks with an answer key, per question.

    Each row has the expected mark, the pipeline's mark, the gap, and whether it is outside the
    tolerance. Uses the model's marks, before any teacher override. Questions the pipeline did not
    mark (struck out) show `got` as None.
    """
    expected = load_expected(path)
    got = {
        (results.student_of(r.item), _norm_q(r.item.question_id)): r.predicted_mark
        for r in results.results(exam)
    }
    rows = []
    for (student, qid), want in sorted(expected.items()):
        have = got.get((student, qid))
        gap = None if want is None or have is None else round(have - want, 2)
        off = (want is None) != (have is None) or (gap is not None and abs(gap) > tolerance)
        rows.append({"student": student, "question": qid, "expected": want, "got": have,
                     "gap": gap, "off": off})  # fmt: skip
    return rows


def _report(rows: list[dict], tolerance: float) -> str:
    marked = [r for r in rows if r["gap"] is not None]
    off = [r for r in rows if r["off"]]
    mae = sum(abs(r["gap"]) for r in marked) / len(marked) if marked else 0.0
    lines = [
        f"{len(marked)} marks compared; mean gap {mae:.2f}; {len(off)} differ by more than {tolerance:g}"
    ]
    for r in off:
        want = "not marked" if r["expected"] is None else f"{r['expected']:g}"
        have = "not marked" if r["got"] is None else f"{r['got']:g}"
        lines.append(f"  {r['student']} Q{r['question']}: expected {want}, got {have}")
    return "\n".join(lines)


CLEAN_COURSES = (
    ("ME1001", "Engineering Mechanics", "teacher_1", (A, B, C, E)),
    ("ME1002", "Thermal and Fluid Sciences", "teacher_1", (A, B, C)),
    ("DS1001", "Data Science", "teacher_1", ()),
    ("LA1001", "Language and Science", "teacher_1", ()),
    ("CS1001", "Programming", "teacher_1", ()),
    ("EE1001", "Circuits", "teacher_2", (A, D)),
)  # A: both teachers; B, C, E: teacher_1 only; D: teacher_2 only; F, G: nowhere yet


def clean(app_data: Path = config.APP_DATA) -> dict[str, str]:
    """Reset to an empty start with no exams, keeping the persona accounts.

    Persona accounts keep their passwords, each student's name is their username, and the courses
    carry a code and a plain name.

    Returns:
        {username: password} for the persona accounts.
    """
    known = _known_passwords(app_data)
    remove(app_data)
    passwords = {}
    for p in PERSONAS:
        wanted = p.password or known.get(p.username) or auth.generate_password(12)
        auth.create_user(
            p.username, p.role, p.username, wanted, by="demo", allow_short=True,
            student_id=p.student_id or None,
        )  # fmt: skip
        passwords[p.username] = wanted
    for code, title, teacher, rolls in CLEAN_COURSES:
        cid = courses.create_course(code, title, teacher, "2026 Autumn", by="demo")
        for roll in rolls:
            courses.enrol(cid, roll, "demo")
    lines = [
        "# Test accounts",
        "",
        "| Username | Role | Password | Student id |",
        "|---|---|---|---|",
    ]
    lines += [
        f"| `{p.username}` | {p.role} | `{passwords[p.username]}` | {p.student_id or ''} |"
        for p in PERSONAS
    ]
    lines += ["", "## Courses", ""]
    lines += [
        f"- **{c} {t}** ({teacher}): {', '.join(r) or 'nobody'}"
        for c, t, teacher, r in CLEAN_COURSES
    ]
    (app_data / "demo_personas.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return passwords


def samples() -> None:
    """Add the sample exams and the sample assignment, so the screens can be tried at once.

    Mechanics Quiz 1 (published, with regrade requests), the Thermodynamics Midterm (marked, files
    are PDFs), Circuits Quiz 1 (published, second teacher) and Fluids Homework 1 (an assignment
    with work handed in). The marks are fabricated, so no model is called. Run after `clean`.
    """
    ids = {c["code"]: c["id"] for t in ("teacher_1", "teacher_2") for c in courses.list_courses(t)}
    for ex in EXAMS:
        if ex.key not in SAMPLES:  # the real-file work is covered by the four cases
            continue
        title, code, kind, owner = SAMPLES[ex.key]
        storage.create_exam(
            title, owner=owner, exam_id=exam_id(ex.key), course_id=ids[code], kind=kind
        )
        if ex.stage != "draft":
            _write_uploads(ex, pdf=ex.key == "thermo")
            _write_run(ex)
    _scenario_publish_and_regrades()
    _sample_homework()


# key -> (title, course code, kind, owner). Two exams are marked, one is published with regrade
# requests, and one assignment has students' work in. The titles say what the work is.
SAMPLES = {
    "mech": ("Mechanics Quiz 1", "ME1001", "exam", "teacher_1"),
    "thermo": ("Thermodynamics Midterm", "ME1002", "exam", "teacher_1"),
    "fluids": ("Fluids Homework 1", "ME1002", "assignment", "teacher_1"),
    "circuits": ("Circuits Quiz 1", "EE1001", "exam", "teacher_2"),
}


def _sample_homework() -> None:
    """Open Fluids Homework 1 for hand-in, with two students' work already submitted."""
    from app.services import submissions

    eid = exam_id("fluids")
    brief = "\n\n".join(
        [
            "Fluids Homework 1",
            "Q1. [5 marks] Find the pressure at 10 m depth in water "
            "(rho = 1000 kg/m^3, g = 9.8 m/s^2).",
            "Q2. [5 marks] State Bernoulli's principle.",
        ]
    )
    key = "\n\n".join(
        [
            "Q1. P = rho g h = 1000 x 9.8 x 10 = 98000 Pa (98 kPa).",
            "Q2. Along a streamline, P + 1/2 rho v^2 + rho g z is constant.",
        ]
    )
    storage.save_uploads(eid, "paper", [("brief.pdf", pdf_bytes(brief))], False, set())
    storage.save_uploads(eid, "reference", [("model_answer.txt", key.encode())], False, set())
    deadline = (date.today() + timedelta(days=14)).isoformat()
    submissions.open_window(
        eid, deadline, "Submit your answers as a PDF, Word or text file.", "teacher_1",
        formats=["documents"],
    )  # fmt: skip
    a_text = "\n\n".join(
        [
            "Q1. The pressure at depth h is P = rho g h, so at 10 m in water it is 98 kPa.",
            "Q2. Bernoulli: P + 1/2 rho v^2 + rho g z is constant along a streamline.",
        ]
    )
    b_text = "\n\n".join(
        [
            "Q1. P = rho g h = 1000 x 9.8 x 10 = 98000 Pa.",
            "Q2. Energy per volume is conserved.",
        ]
    )
    work = {A: ("homework1.pdf", pdf_bytes(a_text)), B: ("homework1.txt", b_text.encode())}
    for roll, file in work.items():
        submissions.submit(eid, roll, [file])
    submissions.collect(eid, "teacher_1")  # the work is already in the answer sheets


def main() -> None:
    """Run the demo command given as the first argument (seed, clean, remove, compare)."""
    action = sys.argv[1] if len(sys.argv) > 1 else ""
    if action == "seed":
        passwords = seed()
        print("Seeded. Credentials and scenarios:", config.APP_DATA / "demo_personas.md")
        for p in PERSONAS:
            sid = f" {p.student_id}" if p.student_id else ""
            print(f"  {p.username:10} {p.role:8} {passwords[p.username]:14}{sid:8} {p.title}")
    elif action == "clean":
        clean()
        if "--samples" in sys.argv:
            samples()
        print(
            "Demo exams removed; accounts, courses and enrolments reset:",
            config.APP_DATA / "demo_personas.md",
        )
    elif action == "remove":
        remove()
        print("Removed the demo exams, courses, students and persona accounts.")
    elif action == "compare" and len(sys.argv) > 2:
        print(_report(compare(sys.argv[2]), 1.0))
    else:
        sys.exit("usage: python -m app.services.demo seed | clean | remove | compare <exam id>")


if __name__ == "__main__":
    main()

# Pipeline demo exam: Strength of Materials mid-semester test

A complete set of teacher files for trying the real marking pipeline, with a human answer key.
Six questions of 5 marks (Q3 has two parts), "answer any five, the best five count", 25 marks counted.

| File | Upload it as |
|---|---|
| `paper.md` | Question paper |
| `model_answer.md`, `rubric.md` | Rubric and model answer (two files, or both inside a zip) |
| `answers/` | Student answer sheets (named by roll number, each with a Name / Roll No header) |
| `answers_messy/` | The same answers with arbitrary file names and imperfect headers: for the identity demo |
| `roster.csv` | Add it to the answers upload; it gives names when accounts are created |
| `expected_marks.csv` | Not uploaded. A person's marks by the rubric, to compare the pipeline against |

## What each student is designed to show

| Student | Behaviour to look for | Expected marks (Q1, Q2, Q3a, Q3b, Q4, Q5, Q6) |
|---|---|---|
| S24001 (student_A) | Excellent on all six. Only the best five count (25 of 25) | 5, 5, 2, 3, 5, 5, 5 |
| S24002 (student_B) | Wrong area in Q3a (used d as the radius) but Q3b is right for that area: follow-through credit | 4, 5, 0, 3, 4, 4, 3 |
| S24003 (student_C) | Average. Q5 has a wrong formula, Q4 and Q6 are thin | 1.5, 5, 2, 3, 3, 1, 2 |
| S24004 (student_D) | Weak. Q2 is the right number with no working: the paper says that earns nothing | 1, 0, 0, 1, 1, 0, 0.5 |
| S24005 (student_E) | Q1 and Q4 written in Hindi. Q3b has a unit slip (1.77 m for 1.77 mm) | 4, 5, 2, 2, 4, 2, 3 |
| S24006 (student_F) | Q5 blank, Q6 crossed out (set "struck out" to `S24006=6`; the demo exam has it preset) | 3, 5, 2, 1, 2.5, 0, not marked |
| S24007 (student_G) | Terse. Q2 has no unit. Q4 is a keyword list (capped). Q6 is off-topic | 3, 4, 2, 3, 2, 4, 0 |
| S24008 (student_H) | Q4 is nonsense text (should score 0 and be treated as incoherent). Q5 is a perfect derivation | 5, 5, 2, 3, 0, 5, 4 |

The paper itself states two exam-wide rules the pipeline should pick up on its own: working is
required for numerical answers, and only the best five questions count. After Prepare, check the
"Rules read from the paper and rubric" box on the Mark tab.

Expected counted totals (best five): A 25, B 20, C 16.5, D 3.5, E 20, F 13.5, G 18, H 24.

## How to run it

1. Sign in as `teacher_1`, create an exam (course ME1003 Strength of Materials), upload the files as in the table above.
2. Settings: pick an AI model. Set "struck out" to `S24006=6`.
3. Mark tab: Prepare, read the marking schemes, then Mark all answers.
4. Compare with the key: `.venv/Scripts/python -m app.services.demo compare <exam id>`.
   The exam id is in the `app_data/exams/` folder name. It lists every mark that differs from
   `expected_marks.csv` by more than 1.
5. Results tab: look at the flagged answers, change a mark, then Publish and sign in as a student.

The seeded `[Demo] Pipeline Test` exam under `teacher_1` already has these files uploaded and the
struck-out setting applied, so you can go straight to step 3.

## The messy set (who wrote what?)

`answers_messy/` has nine sheets, none named like a roll number except by accident. Upload it with
`roster.csv` and Prepare; the Mark tab then lists each sheet. What the pipeline should do:

| Sheet | What is on it | Expected |
|---|---|---|
| `scan_001.md` | Name and roll number, clean | S24001, matched |
| `IMG_0042.md` | Name only | S24002 by name, please check |
| `final answer sheet.md` | Roll `S24O03` (a letter O) | S24003, roll corrected, please check |
| `Divya_quiz.md` | Name and roll, file named by the student | S24004, matched |
| `S24005.md` | No header | S24005 from the file name, please check |
| `sheet_6.md` | Roll S24006 but another student's name | S24006 (the roll wins), name mismatch, please check |
| `x.md` | Name `Student`, nothing else | unknown: you choose (it is S24007) |
| `S24008.md`, `copy of S24008.md` | Two sheets, one roll number | both held: keep one |

S24008 is not in the database yet; the roster uploaded with the sheets introduces them.

A first real run (DeepSeek V4.1 Flash, 7 minutes, free) matched this key to a mean gap of 0.4 marks
per question. Four entries were first written too generously and were corrected after reading the
rubric against the answers; one disagreement is left on purpose (S24005 Q5: the result is stated,
the rubric gives that point to the result, the pipeline withheld it). S24004 Q3b should carry the
flag `follow_through_unchecked`.

The expected marks are one person's reading of the rubric, not ground truth: half a mark either
way is normal, and a disagreement is a reason to look, not proof the pipeline is wrong.

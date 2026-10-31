# The four demo cases

These are four test cases that run through the real web app and the real marking pipeline. Each
case has students (the demo accounts `student_A` to `student_G`, with roll numbers S24001 to
S24007), a question paper, an answer key, and the marks each student was designed to earn. So you
can check the pipeline's marks against what was expected.

## Set up

```bash
uv run python -m app.services.demo clean              # demo accounts and 4 courses, but no exams
uv run python examples/case1_printed/build.py         # builds app_data/case1 from public datasets
uv run python examples/case3_language/build.py        # builds app_data/case3 from public datasets
uv run python -m app.services.cases seed all          # creates the four exams for teacher_1
uv run python -m app.services.cases check case1       # compares marks with the designed ranges
```

Cases 1 to 3 are built from public datasets in `data/raw/`. They are written to the git-ignored
`app_data/` folder, because the dataset licences (for example ScAA, CC BY-NC-SA) do not allow
redistributing the data here. Case 4 is made up, and it lives in `examples/case4_coding/`, so it
works on a fresh clone. Each set-up command prints what it created.

Sign in as `teacher_1` (password `demo1234`) and open the exam.

| Case | Exam (course) | What it shows |
|---|---|---|
| 1 | Case 1: Printed mixed exam (ME1001) | Multiple choice, short answers, an essay and maths proofs in one paper, marked against human grades |
| 2 | Case 2: Handwritten scans (ME1001) | Real handwritten sheets read by an AI reader. The comparison of readers is in `examples/case2_ocr` |
| 3 | Case 3: Language exam (ME1002) | English, Hindi and Marathi questions in one paper |
| 4 | Case 4: Coding and report (ME1003) | Students submit a zip of code and a report, and the code runs in a sandbox |

## Case 1: a printed exam with every question type

- Four multiple-choice questions (from a Mendeley Data Science exam). Code marks them from the key.
- Four short answers (DigiKlausur, neural networks).
- One essay (the aes2 dataset, graded 1 to 6).
- Two olympiad proofs (the imo_grading dataset, graded 0 to 7).

The answers are real answers written by students or by models. Each demo student gets answers whose
human mark follows a designed pattern (see `examples/case1_printed/build.py`).

In the app: Prepare, Mark, then Results. `check case1` compares the marks with the human marks:
multiple choice must match exactly, short answers and the essay must be within one mark, and the
proofs within two.

## Case 2: handwriting

Three real students' handwritten pages (a Mendeley exam with 20 multiple-choice and 15 short
answers) are uploaded as the demo students' scans.

In the app: press *Read the scanned sheets*, check each page against its text on the Mark tab (the
page image is the ground truth), then Prepare and Mark.

`examples/case2_ocr/evaluate.py` compares readers on the same pages. It measures the
multiple-choice letters the student really ticked, the short answers found compared with the ones
the teacher marked, the uncertain spans, the time per sheet, and (with `--mark`) the marks against
the teacher's.

## Case 3: a language exam

Four English questions (from the Mohler dataset, graded 0 to 5), and four Hindi and four Marathi
questions (from ScAA, graded by two annotators who agree). The answers are typed. Marks and
feedback are written in the language of the answer.

## Case 4: code and a report, submitted as a zip

The teacher uploads only the question paper and the answer key (model solutions, rubric and tests).
Each student submits a zip with `q1.py`, `q2.py`, `q3.py` and a report that contains equations.

Seven students are designed:

1. Everything correct.
2. Correct code with a weaker report.
3. A punctuation bug, an off-by-one error and a skipped step.
4. A syntax error and an unfinished function.
5. An endless loop and the wrong exception.
6. Two questions missing.
7. Everything in one `solution.py`, with unnamed files.

In the app, the seed has already submitted the zips. Press *Add the work to the answer sheets*,
then Prepare and Mark. The code runs in the WebAssembly sandbox against the teacher's tests.

## What was measured

These are single runs made on 2026-10-31 in the **development setup**: DeepSeek V4.1 Flash for
marking and free Gemini models for reading. The deployment setup (OpenRouter and the reader order
in `configs/exam.yaml`) has not been measured. Marks vary a little from run to run.

- **Case 4:** 28 answers were marked in about 13 minutes, and **25 of 28 were inside the designed
  range**. The sandbox ran every student's code against the teacher's tests. For student S24003 it
  found 3 of 5 and 1 of 5 passing. The syntax error, the endless loop and the unfinished function
  were all caught and flagged.
  The three misses were all on question 2: S24003 (off by one), S24004 (syntax error) and S24005
  (endless loop). The marker still gave credit for the logic it could read in code that fails the
  tests: 4, 4.5 and 4 out of 6, against a designed 0 to 3. The test results are given to the
  marker and flagged for the teacher, but the rubric rewards visible structure. So a teacher
  should look at flagged code.
- **Case 2 (reading only):** on three real students' sheets (60 multiple-choice ticks and the 38
  short answers the teacher marked), Gemini 3.5 Flash-Lite and Gemini 3.6 Flash both read every
  multiple-choice letter correctly (60 of 60). Both found exactly the 38 answered short questions,
  with none missed and none invented. Flash-Lite took about 11 seconds a sheet and left 7 uncertain
  spans. Gemini 3.6 Flash took about 43 seconds and left none.

## Limits to know about

- **The case data is not final.** Cases 1 to 3 are built mechanically from datasets, and they will
  be curated again before the demo. Maths proofs are long, so Case 1 takes the longest to mark.
- **Marking time.** Only one job runs at a time. Marking the 28 answers of Case 4 took 13 to 18
  minutes, and Case 1 is larger.
- **Reading handwriting is an AI step.** Free reader tiers may keep the images and are rate limited.
  Every scan is shown for correction before marking. Equations on a handwritten page are read as
  text or LaTeX and can be wrong.
- **Code runs only in the standard-library Python sandbox.** Code that needs numpy or other
  libraries, another language, or files is judged by reading it, and is flagged. The sandbox needs
  `tools/sandbox/python.wasm`.
- **Zip files that mix typed files and photos.** The typed files are marked. The photos are kept
  for the teacher but are not read, and the student is not told automatically.
- **Word equations are kept as flat text** (for example `x=-b±b2-4ac2a`). PDF equations are read
  only through the PDF's text layer. A report whose equations are pictures needs the scan path.
- **For typed hand-ins, the student is identified from the account**, not from the file.

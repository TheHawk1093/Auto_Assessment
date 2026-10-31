# Web app (teacher, student, admin)

A Streamlit front end for the `autograde exam` command. The app never marks anything itself. It
starts the command, then shows the files that the command writes.

- Each exam is a folder in `app_data/exams/<id>/` (git-ignored).
- Marking output goes to `output/runs/app_<id>/`, exactly like a command-line run.
- Accounts, mark overrides, regrade requests and the audit log are stored in one SQLite file,
  `app_data/app.db`.
- When you first open the app, it asks you to create the first administrator.

```bash
uv sync --all-extras                     # once
uv run streamlit run app/main.py
uv run pytest tests/test_app*.py         # the app's tests
```

## Layout

| Path | What is there | Rule |
|---|---|---|
| `config.py` | Paths, limits and the name of the CLI config file | Change a location here and nowhere else |
| `text.py` | Unicode (NFC) normalisation, and `\(..\)` to `$..$` for maths | All text that enters or is shown goes through it |
| `services/` | Storage, settings, models, jobs, results, grades, auth, publishing, regrades, overview | No Streamlit imports. Unit-tested |
| `ui/` | `theme.py` (stylesheet), `components.py` (chips, stepper, score card), `rich.py` (maths and Indian-script fonts), `widgets.py` | Reusable pieces of a page |
| `views/` | One module per role. `views/teacher/` has the overview, the workspace and one module per tab | Layout only, no logic |
| `static/katex/` | KaTeX 0.16.11, kept locally with no CDN | Served at `/app/static/katex/` |

## Students, courses and who sees what

A student is a row in `students` with a **unique student id** (the roll number). Answer files,
results, regrade requests and enrolments all carry that id, not the login username. An account is
linked to its student through `users.student_id`.

A **course** is one offering by one teacher. The same course code taught by two teachers is two
courses. A student can be enrolled in any number of courses, under one teacher, the other or both.
An exam belongs to a course.

- **Admin:** creates teachers and admins, resets passwords, disables accounts, and sees every
  course, student and exam.
- **Teacher:** sees only their own courses and exams. A teacher creates courses, enrols a class
  from a roster CSV (`student_id`, `name`, `email`) or one student at a time, marks, changes marks,
  publishes, and answers regrade requests.
- **Student:** has a **grade card** that lists every course they are enrolled in, each under its
  teacher, with a percentage and the overall mean. They can open each published exam and ask for a
  regrade.

A student can see an exam's result only when all three of these are true: the exam is published,
they have marks in it, and (if the exam is in a course) they are enrolled in that course. Every
read path goes through `publishing.can_view`. If a student is dropped from a course, it leaves their
card at once, and their marks are kept. If they are enrolled again, it returns. A student who was
marked in an exam but is not enrolled sees nothing, and the teacher is told on the Publish tab.

Marks are the model's marks, or the teacher's override (`services/grades.py`). The grade card,
every download and the exam page all read through it. So a changed mark, an upheld regrade, a new
enrolment or a publish shows up everywhere on the next read, because nothing on the card is stored.
The model never decides a regrade.

## Who wrote which sheet

Answer sheets do not need a naming convention. The job runs
`autograde exam --directory <app.db> <roster.csv>`, so the pipeline reads the **roll number and
name written on each sheet** and checks them against the student database and the roster uploaded
with the sheets (`src/autograde/intake/identity.py`). In order:

1. An exact roll number wins. The name confirms it, and is flagged if it contradicts it.
2. A roll number that is one character off is corrected if exactly one student is that close, or if
   the name picks one of several.
3. With no usable roll number, a single clear name match among the course's students is used, and
   flagged.
4. If it is still unclear, the AI is shown the header and the few real candidates and may choose
   one of them. The code rejects any other answer.
5. Otherwise the sheet is held for the teacher, with the candidates. A file name is only a weak
   hint. If two sheets belong to one student, both are held.

The Mark tab lists every sheet with what it says, which student it matched, how, and what to look
at. It asks only about the unresolved sheets, and marking waits until they are settled. A setting
allows marking the rest anyway. A teacher's choice is saved and given to the pipeline on later
runs. Results use the resolved student id, so they line up with enrolments and grade cards.

## Scanned and handwritten sheets

Photos and scans are marked in the same way as typed answers, in two steps (`services/scans.py`,
`views/teacher/scans.py` and `autograde scan`).

1. **Read.** On the Upload tab, add images (png, jpg or webp), PDFs (split into pages) or a zip.
   Pages of one sheet are named `name_p1`, `name_p2` and so on, and a single image is one sheet.
   Then press *Read the scanned sheets*. The reader the teacher picks goes first, and the
   fallbacks set in `configs/exam.yaml` (by default another Gemini reader, then Bodhan IndicOCR for
   Indian scripts) are tried in order if it fails or reads doubtfully. The admin can switch a
   reader off. Each sheet becomes `<sheet>.md` next to
   the typed answers, with a Name / Roll No header and `Q1.`, `Q2.` sections. Where the reader was
   unsure of a word, it is written as `[?word?]`. A scanned PDF dropped into the typed answers
   moves to the scans by itself.
2. **Check.** The Mark tab shows each page beside its text, and the text can be edited (*Save
   corrections*, *Read again*, *Remove sheet*). Marking is held until every sheet is read. From
   here, the sheet goes through the same identity matching and marking as any typed answer, so the
   roll number written at the top ties it to the student database.

The free tiers of some readers may keep the images you send. For real student work, use redacted
copies of the pages, or a reader that does not keep them.

## Submissions (assignments)

The teacher uploads only the question paper (one file, several files, or a zip of parts, including
source files) and the answer key (solutions, rubric and tests). The teacher then opens submissions
on the exam and chooses which file types students may upload: documents, source code and
notebooks, photos and scans, or a zip. Enrolled students see **Assignments** on their page and
upload their work, often as one zip containing code and a report. Submitting again replaces the
earlier version until the window closes.

The teacher sees who has and has not submitted, and presses *Add the work to the answer sheets*
(`services/submissions.py` and `services/combine.py`). Each student's files, and the contents of
their zip, become one `<id>.md` under the student's name and roll number from their account:

- Files named for a question (`q1.py`, `Q2a_notes.md`, `q4_report.docx`) are laid out by code as
  `Q1.`, `Q2a.` and `Q4.` sections, with code in fenced blocks.
- Files with any other name (`solution.py`, `report.pdf`) are kept as `## File:` sections. The
  pipeline's splitter then assigns them to questions by reading them.
- Notebooks become their cells. Word equations are kept as flat text. Scanned or photographed pages
  go to the scanned sheets, with the student already known.

The exam is then prepared and marked like any other, so an assignment uses the same settings,
review, publishing and regrades. For coding questions, switch on *Run students' code against
tests* in Settings. The code then runs in a sealed WebAssembly sandbox (Python, standard library
only) against the tests in your answer key (`"tests"`, one `assert` per line), or against tests
that the AI wrote and that were kept only because your model solution passes them. Code that
cannot run (a syntax error, an endless loop, or a library the sandbox lacks) is reported to the
marker as such and is judged by reading it.

## Original pages

When an answer came from a scan, the teacher sees the original page images above the text that the
pipeline marked. This applies in Results, in Regrades and on the Mark tab. The page image is the
ground truth. The text is read from the page only so that the pipeline can mark it. A student sees
their own pages when the exam's policy lets them see their answer.

## Regrade rechecks

For a pending regrade, the teacher may decide alone, or press **Grade autonomously**. The one
answer is then marked again (`autograde recheck`, with the same marking scheme and run settings,
using the exam's model or another) together with the teacher's note, and a proposal (a mark and
feedback) appears. *Use this proposal* fills the decision form, and the teacher edits it and sends
it. The student's reason is never given to the AI, and nothing changes a mark until the teacher
sends the decision.

## Admin database access

The admin's **Database** tab lists every table.

- Names, emails, titles, terms, statuses and marks can be edited in place.
- Rows ticked *delete* are removed, but the database refuses if other records still use them.
- Students, courses and enrolments can be added.
- Passwords are never shown, and the audit log is read-only.
- *Back up the database now* saves a copy in `app_data/backups/`.

Every change is audited (`services/dbadmin.py`).

## Messages

`services/notifications.py` keeps short in-app messages. They appear in the sidebar and refresh
every 20 seconds. They cover: results published, a mark changed, a regrade asked or decided, a
submission received or requested, a job finished, and being added to a course. Nothing is sent
outside the app.

## Renaming

These can be edited: a course's title and term, a student's name and email, an account's display
name, and an exam's title. (Teachers use the Courses tab and the exam's Rename box. The admin uses
Courses and students, and Users.) The identifiers never change: the roll number, the course code,
the username and the exam id.

## Demo accounts

`python -m app.services.demo seed` creates demo data so that every screen can be tried. None of
the accounts is a real person.

- One admin, two teachers and seven students (ids S24001 to S24007, which are roll numbers and are
  separate from the login names).
- Four courses and six demo exams at different stages, each with a story: a high scorer who
  disputes a mark, a student whose regrade was upheld, one whose exam is not yet published, one who
  answers in Hindi with maths, and so on.
- Five of the exams carry made-up marking runs, so no AI model is called. The sixth is ready to
  mark for real.
- Every account uses the password `demo1234`, and the admin is `admin` / `admin`. This is for local
  trials only. Change them before putting the app on a network.

What to try with each account is written in `app_data/demo_personas.md` (git-ignored). Seeding
again is safe, and it rebuilds the demo exams. `python -m app.services.demo remove` deletes exactly
the demo exams (their ids start with `demo-`) and the demo accounts.

## AI models

Each exam stores a model id from `services/models.CATALOGUE`. The teacher picks it in Settings. The
admin can switch options on or off under Admin, AI models.

The app writes a config for each exam: the base `configs/exam.yaml` with the model fields replaced.
The job passes it with `--config`, so the command line still decides how marking works. A model is
offered only when the admin allows it and `OPENROUTER_API_KEY` is set in the environment or in
`.env`. The app checks only that the key exists. It never reads or shows its value.

A different model writes its own marking schemes, because saved schemes are keyed by model.
Changing the model therefore means that Prepare runs again.

## Common changes

- **Add an AI model:** add one `ModelOption` to `services/models.CATALOGUE`.
- **Change the look:** colours, spacing and chip styles are in `ui/theme.py`. The stepper, chips and
  score card are in `ui/components.py`. The accent colour is also `primaryColor` in
  `.streamlit/config.toml`.
- **Change what students may do or see:** edit `DEFAULT_POLICY` in `services/storage.py` and the
  form in `views/teacher/publish.py`. The rules are enforced in `publishing.py` and `regrades.py`.
- **Add a marking setting:** add the flag to `src/autograde/cli/exam.py`, then add one `Field` to
  `services/settings_spec.py`. The Settings tab and the command line then pick it up. A test checks
  that every field's flag exists in the command line.
- **Add or reorder a teacher tab:** write `views/teacher/<name>.py` with a `render(exam_id)`
  function, then edit `TABS` in `views/teacher/__init__.py`.
- **Add an upload box:** add a dict to `SECTIONS` in `views/teacher/upload.py`.
- **Add a role or page:** write `views/<role>.py` with a `render()` function, and add it to `PAGES`
  and `ROLE_PAGES` in `main.py`.
- **Move a block of the settings page:** edit `MARKS_COLUMNS`, or a field's `group`.
- **Change what a download contains:** edit `services/results.py`.

## Maths and scripts

- For answers and feedback, use `ui.rich.rich_text`. It escapes the text, then renders maths with
  KaTeX (`$..$`, `$$..$$`, `\(..\)` and `\[..\]`). For documents, use `ui.rich.markdown`. Tables
  cannot render maths.
- All text is NFC. The joiner characters U+200C and U+200D are kept, because they change Indian-script
  conjuncts. The marking code drops them only when it compares quotes (`pipeline/verify._unicode`).
- Fonts are a stack of Noto Sans and Windows Indic fonts (`FONTS` in `ui/rich.py`). A computer
  without a font for a script shows empty boxes. Install Noto Sans for that script.

## Jobs

`services/jobs.py` starts `autograde exam` through a detached process, `jobwrap`, which records its
process id in `job.json`. A job whose process has died is shown as failed. Cancel stops the whole
process tree. Only one job runs at a time, because marking runs share one rate limit. A regrade
recheck waits for a marking job to finish.

## Not built yet

- Staying signed in after a browser refresh.
- Email delivery of first passwords and notifications.
- Password reset by the user.
- One PDF that holds the sheets of several students. It is read as one sheet, so split it first.
- A guarantee on free reader tiers: they give no promise about quota, and handwriting quality
  varies. That is why every scan is shown for correction before marking.

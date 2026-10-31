# Web app (teacher, student, admin)

Streamlit front end over the `autograde exam` command. Each exam is a folder in
`app_data/exams/<id>/` (git-ignored) and marking output goes to `runs/app_<id>/` like any CLI run.
Accounts, mark overrides, regrade requests and the audit log are in one SQLite file,
`app_data/app.db`. First start: the app asks you to create the first administrator.

```
uv sync --extra app        # once
uv run streamlit run app/main.py
uv run pytest tests/test_app.py tests/test_app_accounts.py
```

## Layout

| Folder | What lives there | Rule |
|---|---|---|
| `config.py` | paths, limits, the CLI config file | change a location here only |
| `text.py` | NFC normalisation, `\(..\)` to `$..$` | everything entering or shown goes through it |
| `services/` | storage, settings spec, models, jobs, results, grades, auth, publishing, regrades, overview | no Streamlit imports; unit-tested |
| `ui/` | `theme.py` (the stylesheet), `components.py` (chips, stepper, score card), `rich.py` (KaTeX + Indic fonts), `widgets.py` | reusable pieces of page |
| `views/` | one module per role; `views/teacher/` has the overview, the workspace and one module per tab | layout only, no logic |
| `static/katex/` | KaTeX 0.16.11 (local, no CDN) | served at `/app/static/katex/` |

## Students, courses and who sees what

A student is a row in `students` with a **unique student id** (the roll number). That id, not the
login username, is what answer files, results, regrade requests and enrolments carry; an account
links to it through `users.student_id`. A **course** is one offering by one teacher (the same code
taught by two teachers is two courses) and a student can be enrolled in any number of them, under
one teacher, the other, or both. An exam belongs to a course.

- **Admin:** creates teachers and admins, resets passwords, disables accounts, sees every course,
  student and exam.
- **Teacher:** sees only their own courses and exams. Creates courses, enrols a class from a roster
  CSV (`student_id`, `name`, `email`) or one by one, marks, changes marks, publishes, answers regrades.
- **Student:** a **grade card** with every course they are enrolled in (each under its teacher, with
  a percentage, and the overall mean of those) and the detail of each published exam, with regrade
  requests. `gradecard.for_student` and `publishing.student_view` are the only read paths and both
  go through `publishing.can_view`: the exam must be published, the student must have marks in it,
  **and** (if the exam is in a course) be enrolled in it. Drop a student and the course leaves their
  card at once, with their marks kept; re-enrol and it returns. A student marked in an exam but not
  enrolled sees nothing, and the teacher is told on the Publish tab.
- Marks are the model's, or the teacher's override (`services/grades.py`). The grade card, every
  download and the exam page read through it, so a changed mark, an upheld regrade, a new enrolment
  or a publish shows up everywhere on the next read. Nothing on the card is stored. The model never
  decides a regrade.

## Who wrote which sheet

Answer sheets need not follow a naming convention. `autograde exam --directory <app.db> <roster.csv>`
(the job passes both) makes the pipeline read the **roll number and name written on each sheet** and
check them against the student database and the roster uploaded with the sheets
(`src/autograde/intake/identity.py`):

1. an exact roll number wins (the name confirms it, or is flagged if it contradicts it);
2. a roll number off by one character is corrected if exactly one student is that close, or the name
   picks one of several;
3. with no usable roll number, a single clear name match among the course's students (flagged);
4. only if still ambiguous, the model sees the header and the few real candidates and may choose one
   of them (code rejects any other answer);
5. otherwise the sheet is held for the teacher with the candidates. A file name is only a weak hint,
   and two sheets for one student are both held.

The Mark tab lists every sheet with what it says, who it matched, how, and what to look at, and
asks about only the unresolved ones; marking waits until they are settled (a setting allows marking
the rest anyway). A teacher's choice is saved and given to the pipeline on later runs. Results use
the resolved student id, so they line up with enrolments and grade cards.

## Scanned and handwritten sheets

Photos and scans are marked the same way as typed answers, in two steps (`services/scans.py`,
`views/teacher/scans.py`, `autograde scan`):

1. **Read.** On the Upload tab add images (png, jpg, webp), PDFs (split into pages) or a zip. Pages of
   one sheet are named `name_p1`, `name_p2`; a lone image is a sheet. Pick a reader (Gemini free
   tier, or Claude through the CLI; the admin can switch readers off) and press *Read the scanned
   sheets*. Each sheet becomes `<sheet>.md` beside the typed answers: a Name / Roll No header, then
   `Q1.`, `Q2.` sections, with `[?word?]` where the reader was unsure. A scanned PDF dropped into the
   typed answers moves to the scans by itself.
2. **Check.** The Mark tab shows each page beside its text, editable (*Save corrections*, *Read
   again*, *Remove sheet*). Marking is held until every sheet is read. From here the sheet goes
   through the same identity matching and marking as any typed answer, so the roll number written
   at the top is what ties it to the student database.

Free reader tiers may keep the images. Use Claude, or redacted copies, for real student work.

## Student hand-ins

The teacher opens a window on an exam (Upload tab, optional deadline and instructions). Enrolled
students then see **Hand in work** on their page and upload documents or photos; handing in again
replaces the earlier version until the window closes. The teacher sees who has and has not handed in
and presses *Add the work to the answer sheets* (`services/submissions.py`): typed work becomes
`<id>.md` with the student's name and roll number from their account, photos become scanned sheets
with the identity already known (so it never depends on handwriting), and the exam is then prepared
and marked as usual. Collecting again after a late hand-in replaces, never duplicates.

## Regrade rechecks

On a pending regrade the teacher may decide alone, or press *Ask the pipeline*: the one answer is
marked again (`autograde recheck`, same marking scheme and run settings, the exam's model or another)
with the teacher's note, and a proposal (mark and feedback) appears. *Use this proposal* fills the
decision form; the teacher edits and sends. The student's reason is never given to the model, and
nothing changes a mark until the teacher sends the decision.

## Messages

`services/notifications.py` keeps short in-app messages, shown in the sidebar (refreshing every 20
seconds): results published, a mark changed, a regrade asked or decided, a hand-in received or
requested, a job finished, being added to a course. Nothing is sent outside the app.

## Renaming

Course title and term, student name and email, an account's display name and an exam's title can be
edited (teacher: Courses tab and the exam's Rename box; admin: Courses and students, Users). The
identifiers never change: roll number, course code, username, exam id.

## Test personas

`python -m app.services.demo seed` creates one admin, two teachers and seven students (unique ids
S24001 to S24007, a roll number separate from the login), four courses and six demo exams, each with a
story (a high scorer who disputes a mark, a student whose regrade was upheld, one whose exam is not
published yet, one answering in Hindi with maths, ...) and four demo exams at different stages. It
writes fabricated marking runs, so no model is called. Credentials and what to try for each persona
are in `app_data/demo_personas.md` (git-ignored). Seeding again keeps passwords and rebuilds the demo
exams; `python -m app.services.demo remove` deletes exactly the demo exams (ids start `demo-`) and
the persona accounts.

## AI models

Each exam stores a model id from `services/models.CATALOGUE`. The teacher picks it in Settings; the
admin switches options on or off in Admin, AI models. The app writes a per-exam config (the base
`configs/exam.yaml` with the model fields replaced) and the job passes it as `--config`, so the CLI
still decides how marking works. A model is offered only if the admin allows it and this machine
can run it (Claude CLI present, API key present in the environment or `.env`; the key itself is
never read or shown). OpenRouter options are listed but locked until an admin switches them on, and
even then need `OPENROUTER_API_KEY`. A different model writes its own marking schemes (the cache is
keyed by model), so changing it means Prepare runs again.

## Common changes

- **Add an AI model:** one `ModelOption` in `services/models.CATALOGUE`.
- **Change the look:** colours, spacing and chip styles are in `ui/theme.py`; the stepper, chips and
  score card are in `ui/components.py`. The accent colour is also `primaryColor` in
  `.streamlit/config.toml`.

- **Change what students may do or see:** `DEFAULT_POLICY` in `services/storage.py` and the form
  in `views/teacher/publish.py`; enforcement is in `publishing.py` and `regrades.py`.

- **Add a marking setting:** add the flag to `src/autograde/cli/exam.py`, then one `Field` in
  `services/settings_spec.py`. The settings tab and the command line pick it up. A test checks
  that every field's flag exists in the CLI.
- **Add or reorder a teacher tab:** write `views/teacher/<name>.py` with `render(exam_id)`, edit
  `TABS` in `views/teacher/__init__.py`.
- **Add an upload box:** add a dict to `SECTIONS` in `views/teacher/upload.py`.
- **Add a role or page:** `views/<role>.py` with `render()`, add it to `PAGES` and `ROLE_PAGES` in `main.py`.
- **Move a block of the settings page:** edit `MARKS_COLUMNS` or a field's `group`.
- **Change what a download contains:** `services/results.py`.

## Maths and scripts

- Answers and feedback: `ui.rich.rich_text` (escaped, then KaTeX auto-render; `$..$`, `$$..$$`,
  `\(..\)`, `\[..\]`). Documents: `ui.rich.markdown`. Tables cannot render maths.
- All text is NFC. The joiners U+200C/U+200D are kept (they change Indic conjuncts); the marking
  backend drops them only to compare quotes (`pipeline/verify._unicode`).
- Fonts: a stack of Noto Sans and Windows Indic fonts in `ui/rich.py` (`FONTS`). A machine
  without an Indic font shows boxes; install Noto Sans for the script.

## Jobs

`services/jobs.py` starts `autograde exam` through a detached `jobwrap`, which records its process
id in `job.json`. A job whose process died shows as failed, Cancel kills the process tree, and only
one job runs at a time (Goedel allows four concurrent requests in total).

## Not built yet

- Staying signed in across a browser refresh, email delivery of first passwords and notifications,
  password reset by the user, cost and model settings in Admin.
- One PDF holding the sheets of several students is read as one sheet; split it first.
- Free reader tiers (Gemini) may keep the images and give no guarantee of quota; handwriting
  quality varies, which is why every scan is shown for correction before marking.
- Only one job runs at a time (a regrade recheck waits for a marking job to finish).

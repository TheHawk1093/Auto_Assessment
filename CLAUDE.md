# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Project plan and decisions: docs/internal/PROJECT.md. Usage, switches, experiment workflow: docs/USAGE.md (quick start: README.md). Design evidence and results by section: docs/DESIGN.md. Datasets: docs/DATASETS.md.

## Commands
- Tests: `.venv/Scripts/python -m pytest`; one test: `.venv/Scripts/python -m pytest tests/test_verify.py::test_name`. Tests use fake LLM clients (`tests/fakes.py`), no network.
- Web app: `.venv/Scripts/streamlit run app/main.py` (layout, how to add a setting or tab: `app/README.md`). Install with `uv pip install --python .venv/Scripts/python.exe -e ".[app]"`; use uv, the venv has no pip.
- Lint: `.venv/Scripts/ruff check src tests` and `ruff format src tests`
- Run: `.venv/Scripts/autograde run --dataset digiklausur --split dev -n 24 --mode pipeline --name <run>`

## Marking a real exam
- `autograde --config configs/exam.yaml exam --paper P --reference R --answers A --name N` (see docs/DESIGN.md section 20). Always pass the config path with its `.yaml` extension: a missing config file is an error.
- Goedel allows 4 concurrent requests in total, so do not run two DeepSeek jobs at once.

## Architecture (big picture)
- Flow per item: `pipeline/rubric.py` (marking scheme written once per question, self-tested, cached under `rubrics/<client_name>/<variant>/`) -> `read.py` (optional first pass on the answer alone) -> `grade.py` (per-point verdicts with quotes) -> `verify.py` (quote checks, form gate, code sums marks, one retry) -> `feedback.py`. `run.py` drives this in parallel with resume; `baseline.py` is the one-prompt comparison; `cascade.py`/`vote.py` add escalation and second-model flags.
- `llm/` exposes one `ask(system, user, PydanticModel)` interface. `build_client` in `llm/__init__.py` picks the backend from config (`claude_cli`, `anthropic`, `openrouter`, `goedel`). `client_name` (backend-model-effort) keys the stored schemes, so changing model or effort changes which `rubrics/` folder is used.
- Config is YAML loaded into pydantic `Settings` (`config.py`); `--config configs/x.yaml` is a global flag placed before the subcommand. Separate `llm`, `judge`, `student` clients exist; the judge must be a different provider from the grader. Most `configs/*.yaml` are one-off experiment variants; `default.yaml` is the baseline.
- Prompts are selected by config switches (policy, feedback variant, rubric level), so a behaviour change usually means a new prompt file plus a switch in `PipelineConfig`, not new code paths. Prompts sit in stage folders under `prompts/` and are found by file name (unique across folders). Anything about a language other than English lives only in `prompts/language/` and `localize.py`; English prompts never mention it. The solid scheme writer takes a style (`rubric_variant: solid.core` adds `rubric.style.core`) and `feedback_variant: concrete` is an opt-in feedback wording; neither is the default (DESIGN.md section 22).
- `intake/` turns teacher files (paper, reference, answers) into `Item`s for the `exam` command; `evaluation/` holds metrics and the extra tests (stress, revision, transfer, sensitivity); `viewer/` builds `report.html`; `ocr/` is a separate handwriting track.
- `scripts/` holds the shell chains of past experiments and `configs/experiments/<group>/` the one-off configs (only `default`, `exam`, `poc` and `models/` are live). `tools/ocr/` holds standalone OCR scripts (not part of the package); `tools/ocr/engines/` needs the separate git-ignored `.venv-ocr`. Lint with `ruff check src tests tools app`.
- `autograde run` also appends to `experiments/log.jsonl` and rebuilds `experiments/RESULTS.md`; it commits and tags the code only with `--commit`.
- Question kinds (`schemas.Kind`: short, essay, maths, mcq, numeric, code, diagram) are handled by code checks in `pipeline/checks.py`, which `mark_item` runs before marking: `objective.py` (multiple choice, marked by code with no model call, `RubricStore.get` skips the writer), `numeric.py` (value, unit conversion and tolerance; a rubric point with a `numeric` spec is decided by code, not the marker), `codecheck.py` (syntax fact; the teacher's tests run only with `pipeline.code_exec`, which executes untrusted code and needs a container), `figure.py` (a vision model describes the drawing as text; the marker never sees the image, and the answer is flagged). Each kind has optional prompts `grade.kind.<kind>`, `feedback.kind.<kind>`, `rubric.solid.<kind>`.
- Teacher controls live in `TeacherInputs` (`config.py`): `strictness`, `partial_credit`, `mark_step` (any step, e.g. 0.2; partial marks are the model's figure rounded to the step, and `snap_grading` rounds everything at the end), `notes` and `question_notes` (reach the scheme writer, the marker and the feedback writer), `follow_through` (multi-part: `Item.earlier` holds the earlier parts' answers, set in `intake/exam.py`). The `exam` command exposes them as flags.
- Figures in answer or reference files (markdown image, `[figure: path]`, or a picture inside a .docx) are anchored to absolute paths on read (`intake/figures.py`) and split from the words when items are built (`intake/exam.py`); a drawing answer becomes kind `diagram`.
- Student code runs only in `pipeline/sandbox.py`: `wasm` (default; wasmtime + `tools/sandbox/python.wasm`, standard library only, so code importing numpy is not run and is flagged `code_needs:<module>`), `docker`, or `process` (trusted code only). `pipeline/codetests.py` writes tests for code questions that have none and keeps only those a reference solution passes (`tests_generated` flag). The wasm path is untested against the real binary: run `AUTOGRADE_REAL_SANDBOX=1 pytest tests/test_sandbox_real.py` once (see `tools/sandbox/README.md`).
- Datasets `scaa_marathi` and `circuit_hw` (`datasets/circuit.py`: marks out of 100, only tune/validate students, pages transcribed first with `python -m autograde.datasets.circuit`; the sealed benchmark students are never loaded).
- `llm/gemini.py` is a text backend on the free-tier allow-list in `ocr/hosted.py`; `gemini-3.1-pro-preview` has no free quota on our key. `feedback_language` makes feedback come out in the student's language. Evidence quotes are compared after Unicode normalisation (`verify._unicode`), which Indic scripts need.
- `pipeline/review.py` lists answers worth a person's look (`autograde review --name R`, "Worth a look" in the report); optional, the marks stand without it. `autograde robustness --name R` re-marks rewritten answers (spelling, paraphrase, half the answer, ...) against a re-marking control; `python -m autograde.ocr.faithful` checks that a reader copies a student's mistakes. Results and what they mean: DESIGN.md section 25.
- Exam-wide rules come from the documents, not flags: `intake/rules.py` (`extract_rules`, prompt `intake.rules`) reads the paper's instructions and the rubric once per exam into `ExamRules` (working required, part-mark rule, carry-through, other notes) and `apply_rules` turns them into `TeacherInputs`; the teacher's flags win, `--ignore-rubric-rules` switches it off, and the rules are listed at the top of `schemes.md`. `partial_credit: stated` means only levels the rubric names (a point without levels is all or nothing); `working_required` zeroes a numerical answer whose reading says `working_shown: false` (`verify.apply_working_gate`). Best-of-n: `intake/counting.py` (`count_best` from the paper or `--count-best`, `--struck-out STUDENT=Q` skips marking that question; totals only, nothing cached changes). DESIGN.md section 26.
- Who wrote a sheet: `intake/identity.py` reads the roll number and name from the sheet itself (not the file name) and checks them against a student directory (`--directory app.db roster.csv --course-id N`): exact roll, roll off by one character, name, then a model pick among real candidates; what stays ambiguous is held (`identity.json`, `--identity-fixes`, `--allow-unresolved`). `load_answers_identified` in `intake/answers.py`; plain `load_answers` (file stem) is still used without a directory. Two sheets for one student are both held.
- Handwritten work: `autograde scan` reads page images into `<sheet>.md` (Name / Roll No header, `Q<n>.` sections) with a free or Claude reader (`ocr/answersheet.py`, prompt `ocr.answersheet`); the app's scans, student hand-ins (`app/services/submissions.py`) and `autograde recheck` (one answer re-marked with a teacher note, proposal only) feed the same `exam` command.
- `autograde judge-sheet` / `judge-agreement` check the feedback judge against a person who reads the language (`artifacts/judge_check/`).

- `app/` is the Streamlit web app: login with roles, teacher flow (upload, settings, mark, mark overrides, publish, regrade inbox), student results and regrade requests, admin users. State: exam folders plus `app_data/app.db` (users, students with unique ids, courses, enrolments, overrides, regrades). A student's grade card spans every course they are enrolled in, under any teacher; `publishing.can_view` (published, marked, enrolled) is the one visibility gate. Marking settings are defined once in `app/services/settings_spec.py` and become `autograde exam` flags; it runs the CLI as a detached job, so the CLI stays the single source of marking behaviour.

## Conventions
- Backend and key policy: DeepSeek uses `backend: goedel` (free, `GOEDEL_API_KEY`); Haiku/Sonnet use `claude_cli`; do not spend the OpenRouter balance. Keys live in git-ignored `.env`/`API.md`; never print them.
- Feedback is mandatory for every non-perfect answer; `with_feedback: false` is only a measurement shortcut in test configs.
- Python 3.11, type hints, pydantic models in `schemas.py`, no agent framework.
- All prompts live under `src/autograde/prompts/<stage>/` and all marking schemes in `rubrics/`; code does arithmetic and checks, the model does judgement.
- Split dev/test by question. Never tune on test.
- Runs and data are git-ignored (`runs/`, `data/`). EngSAF is benchmark-only: never tune on it.
- Write multi-line files with the Write tool; bash heredocs holding quotes and backslashes fail in this shell. A `\n` inside a heredoc becomes a real newline, so for code with escapes use the Edit tool, not a shell-written patch script.

## Do not read (large or generated)
- `artifacts/Project_Tracker/tracker.html`, `template.html`, `runs/*/report.html`, `runs/*/results.jsonl`, `data/`.
  Use `metrics.json`, `usage.json` or the report's source builder instead.

## Updating the tracker (cheap)
Edit only `artifacts/Project_Tracker/tracker.json`, then run `python artifacts/Project_Tracker/build.py`.
Result numbers are read from `runs/<name>/metrics.json`; set the two run names under `compare`.

## Proof of concept first
- Cheap check on every dataset, simple to hard: `autograde --config configs/poc.yaml poc -n 8 --baseline` (Haiku, low effort, about 25 cents). Run long tests only after this looks right.

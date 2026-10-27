# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Project plan and decisions: PROJECT.md. Usage, switches, experiment workflow: README.md. Design evidence and results by section: DESIGN.md. Datasets: DATASETS.md.

## Commands
- Tests: `.venv/Scripts/python -m pytest`; one test: `.venv/Scripts/python -m pytest tests/test_verify.py::test_name`. Tests use fake LLM clients (`tests/fakes.py`), no network.
- Lint: `.venv/Scripts/ruff check src tests` and `ruff format src tests`
- Run: `.venv/Scripts/autograde run --dataset digiklausur --split dev -n 24 --mode pipeline --name <run>`

## Marking a real exam
- `autograde --config configs/exam.yaml exam --paper P --reference R --answers A --name N` (see DESIGN.md section 20). Always pass the config path with its `.yaml` extension: a missing config file is an error.
- Goedel allows 4 concurrent requests in total, so do not run two DeepSeek jobs at once.

## Architecture (big picture)
- Flow per item: `pipeline/rubric.py` (marking scheme written once per question, self-tested, cached under `rubrics/<client_name>/<variant>/`) -> `read.py` (optional first pass on the answer alone) -> `grade.py` (per-point verdicts with quotes) -> `verify.py` (quote checks, form gate, code sums marks, one retry) -> `feedback.py`. `run.py` drives this in parallel with resume; `baseline.py` is the one-prompt comparison; `cascade.py`/`vote.py` add escalation and second-model flags.
- `llm/` exposes one `ask(system, user, PydanticModel)` interface. `build_client` in `llm/__init__.py` picks the backend from config (`claude_cli`, `anthropic`, `openrouter`, `goedel`). `client_name` (backend-model-effort) keys the stored schemes, so changing model or effort changes which `rubrics/` folder is used.
- Config is YAML loaded into pydantic `Settings` (`config.py`); `--config configs/x.yaml` is a global flag placed before the subcommand. Separate `llm`, `judge`, `student` clients exist; the judge must be a different provider from the grader. Most `configs/*.yaml` are one-off experiment variants; `default.yaml` is the baseline.
- Prompts are selected by config switches (policy, feedback variant, rubric level), so a behaviour change usually means a new `prompts/*.md` file plus a switch in `PipelineConfig`, not new code paths.
- `intake/` turns teacher files (paper, reference, answers) into `Item`s for the `exam` command; `evaluation/` holds metrics and the extra tests (stress, revision, transfer, sensitivity); `viewer/` builds `report.html`; `ocr/` is a separate handwriting track.
- `tools/` holds standalone OCR scripts (not part of the package); `tools/ocr_engines/` needs the separate git-ignored `.venv-ocr`. Lint with `ruff check src tests tools`.
- `autograde run` also appends to `experiments/log.jsonl`, rebuilds `experiments/RESULTS.md`, and commits plus tags the code; pass `--no-commit` for throwaway runs.

## Conventions
- Backend and key policy: DeepSeek uses `backend: goedel` (free, `GOEDEL_API_KEY`); Haiku/Sonnet use `claude_cli`; do not spend the OpenRouter balance. Keys live in git-ignored `.env`/`API.md`; never print them.
- Feedback is mandatory for every non-perfect answer; `with_feedback: false` is only a measurement shortcut in test configs.
- Python 3.11, type hints, pydantic models in `schemas.py`, no agent framework.
- All prompts live in `src/autograde/prompts/*.md` and all marking schemes in `rubrics/`; code does arithmetic and checks, the model does judgement.
- Split dev/test by question. Never tune on test.
- Runs and data are git-ignored (`runs/`, `data/`). EngSAF is benchmark-only: never tune on it.
- Write multi-line files with the Write tool; bash heredocs holding quotes and backslashes fail in this shell.

## Do not read (large or generated)
- `artifacts/Project_Tracker/tracker.html`, `template.html`, `runs/*/report.html`, `runs/*/results.jsonl`, `data/`.
  Use `metrics.json`, `usage.json` or the report's source builder instead.

## Updating the tracker (cheap)
Edit only `artifacts/Project_Tracker/tracker.json`, then run `python artifacts/Project_Tracker/build.py`.
Result numbers are read from `runs/<name>/metrics.json`; set the two run names under `compare`.

## Proof of concept first
- Cheap check on every dataset, simple to hard: `autograde --config configs/poc.yaml poc -n 8 --baseline` (Haiku, low effort, about 25 cents). Run long tests only after this looks right.

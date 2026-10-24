# Working notes for Claude

Project plan and decisions: PROJECT.md. Usage: README.md.

## Commands
- Tests: `.venv/Scripts/python -m pytest`
- Lint: `.venv/Scripts/ruff check src tests` and `ruff format src tests`
- Run: `.venv/Scripts/autograde run --dataset digiklausur --split dev -n 24 --mode pipeline --name <run>`

## Conventions
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

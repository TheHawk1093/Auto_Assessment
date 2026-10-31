# Branching plan (agreed, to run after development is complete)

Decisions from the owner:
- Fresh `main` and fresh `dev`, no old history. The old history is kept only as the local branch
  `legacy-history` (created 2026-10-31, never pushed). The remote repo is private.
- Commits go in sequence, one module group at a time, so the history reads like a build-up.
- `main` = bare-minimum deployable pipeline. `dev` = `main` + tuning material. Same structure.
- Data on `dev`: short credits doc (`docs/DATA_CREDITS.md`), only helpful datasets, as many sample
  rows as git can sensibly hold (no file over a few MB). No full raw datasets.
- ME5309 course data: neither branch.

## main commit sequence (proposal)
1. Project scaffold: pyproject, uv.lock, LICENSE, .gitignore, .env.example, CONTRIBUTING
2. Core contracts: `schemas.py`, `config.py`, `localize.py`, `textutil.py`, prompts loader
3. LLM backends: `llm/` (base, claude_cli, anthropic, openrouter, goedel, gemini, mock) + tests
4. Prompts (`prompts/`)
5. Marking pipeline: rubric, read, grade, verify, feedback + tests
6. Question-kind checks: objective, numeric, code, sandbox, figure + `tools/sandbox` + tests
7. Intake: paper, reference, answers, rules, identity, counting + tests
8. CLI (`cli/`: exam, scan, recheck) + viewer + configs (default, exam, mock, models) + examples
9. Web app (`app/`, `.streamlit/`) + tests
10. Docs: README, WORKFLOW, USAGE, DESIGN, diagram, CI workflow

## dev adds on top (sequence)
1. `.gitignore` override (un-ignore dev content), dev README
2. `datasets/` loaders, `autograde download`, `datasets/samples/`, `docs/DATA_CREDITS.md`, `docs/DATASETS.md`
3. `evaluation/` (metrics, stress, robustness, revision, transfer, ...) and `ocr/`
4. Curated `output/rubrics/`, `configs/experiments/`, `experiments/`, `scripts/`, `artifacts/` tracker
5. Dev docs: tuning workflow, experiment log, DESIGN evidence

Open question to settle before branching: `evaluation/`, `ocr/` and `datasets/` are imported by the
CLI. Either move them behind lazy imports (so `main` can omit them) or keep them on `main`.

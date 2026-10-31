# Contributing

Thank you for helping. This page tells you how to set up, what the code expects, and what must
never be committed.

## Set up

```bash
uv sync --all-extras          # installs the app, the code sandbox and the dev tools
uv run pytest                 # tests use scripted fake models, so no network or keys are needed
uv run ruff check src tests app && uv run ruff format src tests app
```

Before you change anything, read the [codebase guide](docs/GUIDE.md).

## What the code expects

- Python 3.11, with type hints and Google-style docstrings. Ruff enforces the docstring rules.
- Code does the arithmetic and the checks. The AI model only makes judgements.
- Every instruction given to an AI model is a text file in `src/autograde/prompts/<stage>/`. A
  change in behaviour is usually a new prompt file plus a switch in `PipelineConfig`, not a new
  code path.
- Add a test for every change. Tests must run offline.
- Tune only on `dev` questions. Never tune on `test` data or on EngSAF.

## What must never be committed

Keys, student data and anything generated. These are already git-ignored: `.env`, `data/`,
`output/` and `app_data/`. Check `git status` before you commit.

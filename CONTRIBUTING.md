# Contributing

```bash
uv sync --all-extras          # runtime, app, sandbox and dev tools
uv run pytest                 # tests use fake clients: no network, no keys
uv run ruff check src tests app && uv run ruff format src tests app
```

- Python 3.11, type hints, Google-style docstrings (ruff enforces them with `D` rules).
- Prompts live in `src/autograde/prompts/<stage>/`; a behaviour change is usually a new prompt file
  plus a switch in `PipelineConfig`, not a new code path.
- Code does arithmetic and checks; the model does judgement.
- Tune on `dev` questions only. Never tune on `test` or on EngSAF.
- Never commit keys or student data. `data/`, `runs/`, `app_data/` and `.env` are git-ignored.

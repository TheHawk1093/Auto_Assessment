# autograde

Grades student answers against model answers with a marking scheme, then writes feedback. Runs with no human step. Plan and decisions: [PROJECT.md](PROJECT.md). Datasets: [DATASETS.md](DATASETS.md).

## Setup (Python 3.11+)

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/Scripts/python.exe -e ".[dev]"     # add ,anthropic for the API backend
.venv/Scripts/autograde download                                  # DigiKlausur, SAF, Mohler -> data/raw
.venv/Scripts/python -m pytest
```

## Use

```bash
# one-prompt baseline vs the full pipeline, same sample
autograde run --dataset digiklausur --split dev -n 24 --mode baseline --name dk_baseline
autograde run --dataset digiklausur --split dev -n 24 --mode pipeline --name dk_pipeline
autograde judge --name dk_pipeline     # scores the feedback with a second model
autograde report --name dk_baseline
autograde view --name dk_pipeline      # rebuild runs/dk_pipeline/report.html
```

Open `runs/<name>/report.html` to read the samples (question, model answer, student answer with quoted evidence highlighted, our marks vs the teacher's, feedback; filter to answers that differ from the teacher). `run` and `judge` rebuild it automatically.

Outputs go to `runs/<name>/`: `report.html`, `results.jsonl` (marks, per-point verdicts, feedback, flags), `metrics.json`, `usage.json`. Interrupted runs resume where they stopped. Marking schemes are cached in `data/cache/rubrics/`.

Models are set in `configs/default.yaml`. `claude_cli` uses your Claude Code login (good for early tests, one process per call). `anthropic` uses the API and needs `ANTHROPIC_API_KEY`.

## How it works

```
Item -> RubricStore (write once per question, self-test, cache)
     -> mark_answer (per-point verdicts + quotes) -> verify (quotes real, limits, code sums marks; one retry, then repair)
     -> write_feedback (from the checked marking only)
```

| Path | Purpose |
|---|---|
| `src/autograde/schemas.py` | Data contracts |
| `src/autograde/datasets/` | Loaders, dev/test split by question, downloader |
| `src/autograde/llm/` | One `ask(system, user, PydanticModel)` interface; CLI and API backends |
| `src/autograde/pipeline/` | rubric, grade, verify, feedback, baseline, run |
| `src/autograde/prompts/` | Prompt text as markdown |
| `src/autograde/evaluation/` | Mark metrics, feedback judge |
| `src/autograde/viewer/` | `report.html` template and builder |

Data splits: a question goes to `dev` or `test` by a hash of its id, so no question appears in both. Tune on `dev`; run `test` rarely.

## Framework choice

No agent framework (LangGraph, Agents SDK). The flow is a fixed sequence of model calls with code checks between them, so plain functions are simpler to test and debug. Revisit if the flow needs branching or tool use (for example a calculator in stage 2).

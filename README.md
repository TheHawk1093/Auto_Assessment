# autograde

An automatic grader for STEM answer sheets. Give it a question paper, a reference (model answers and/or a rubric) and the students' answers. It writes a marking scheme for each question, marks every answer **point by point with quoted evidence**, checks the marks with code, and writes feedback for every student who lost marks. There is no human step in the loop.

![Workflow](docs/images/workflow.svg)

## Key features

- **Marking schemes written once per question**, self-tested (the model answer must score full marks, a "don't know" must score zero) and cached.
- **Evidence-backed marks.** Every awarded point carries a quote from the student's answer. Code checks that the quote exists, that marks sum correctly and that limits hold; one retry, then repair.
- **Code, not the model, does arithmetic.** Multiple choice, numeric answers (units, tolerance) and code questions are settled by deterministic checks (`pipeline/checks.py`).
- **Mandatory feedback** for every non-perfect answer, built from the verified marking only.
- **Teacher controls**: strictness, partial-credit granularity, mark step, free-text notes, follow-through for multi-part questions. Exam-wide rules are read from the paper and rubric.
- **Pluggable models**: Claude (CLI or API), DeepSeek via Goedel, OpenRouter, Gemini, and an **offline `mock` backend** so everything runs with no API key.
- **Web app** (Streamlit): teacher flow (upload, settings, mark, override, publish), student results and regrade requests, admin.
- **Evaluation tooling**: agreement with teacher marks, stress, robustness, revision and transfer tests; handwriting OCR track.

## Setup

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
git clone <this-repo> && cd Auto_Assessment
uv sync --all-extras          # creates .venv with runtime, web app, sandbox and dev tools
cp .env.example .env          # only if you will use a real model backend; add your keys
uv run pytest                 # all tests run offline
```

Minimal install (CLI only): `uv sync --no-dev`. Optional extras: `anthropic`, `files` (PDF reading), `sandbox` (run student code in WebAssembly), `app`.

## Quick start (no API key)

```bash
uv run autograde --config configs/mock.yaml exam \
  --paper examples/exam_demo/paper.json \
  --reference examples/exam_demo/reference_model_only.json \
  --answers examples/exam_demo/answers --name demo
```

Open `runs/demo/schemes.md` (the marking schemes), `runs/demo/marks.csv` and `runs/demo/students/<student>.md` (marks and feedback). The mock backend marks by word overlap: it proves the pipeline runs, it is **not** a real grader.

## Marking a real exam

Pick a real backend in the config (`configs/exam.yaml` uses DeepSeek via Goedel; `llm.backend: claude_cli` uses your Claude Code login; `anthropic` needs `ANTHROPIC_API_KEY`):

```bash
uv run autograde --config configs/exam.yaml exam \
  --paper paper.md --reference reference.md --answers answers/ \
  --name quiz1 --strictness moderate --note "units are required"
```

`--paper` takes txt, md, docx, text pdf or json; `--answers` is a folder with one file per student (or a JSON file). Always pass the config with its `.yaml` extension. See [docs/USAGE.md](docs/USAGE.md) for every flag and switch.

## Web app

```bash
uv run streamlit run app/main.py
```

The first start asks you to create an administrator. Layout and how to add a setting or tab: [app/README.md](app/README.md).

## Project layout

| Path | Purpose |
|---|---|
| `src/autograde/schemas.py`, `config.py` | Data contracts and YAML-backed settings |
| `src/autograde/llm/` | One `ask(system, user, PydanticModel)` interface and the backends (`mock` included) |
| `src/autograde/intake/` | Teacher files (paper, reference, answers, identity, rules) to `Item`s |
| `src/autograde/pipeline/` | rubric, read, grade, verify, feedback, checks (objective, numeric, code, figure), run |
| `src/autograde/prompts/` | Every prompt as markdown, grouped by stage |
| `src/autograde/evaluation/` | Metrics and extra tests (stress, revision, transfer, robustness) |
| `src/autograde/cli/` | Command line, one module per group |
| `src/autograde/viewer/`, `ocr/`, `datasets/` | `report.html` builder, handwriting track, dataset loaders |
| `app/` | Streamlit web app (services are UI-free and unit-tested) |
| `configs/` | `default`, `exam`, `mock`, `poc`, `ocr_free`, `models/` |
| `examples/` | Small exams used by the demo and tests |
| `tests/` | pytest suite with scripted fake models: no network |
| `tools/` | Standalone OCR scripts and the WebAssembly code sandbox |
| `docs/` | [Workflow](docs/WORKFLOW.md), [usage reference](docs/USAGE.md), [design evidence](docs/DESIGN.md), [datasets](docs/DATASETS.md) |

Data (`data/`), run output (`runs/`), app state (`app_data/`) and secrets (`.env`) are git-ignored. Provide your own exam data; see [docs/DATASETS.md](docs/DATASETS.md).

## How it works

[docs/WORKFLOW.md](docs/WORKFLOW.md) walks through the four stages (intake, marking scheme, marking, feedback) with the diagram above. The design rationale and measured results are in [docs/DESIGN.md](docs/DESIGN.md).

## Development

```bash
uv run pytest --cov            # tests with coverage
uv run ruff check src tests app && uv run ruff format src tests app
```

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).

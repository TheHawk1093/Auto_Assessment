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

Mark a whole exam from its files (see DESIGN.md section 20):

```bash
autograde --config configs/exam.yaml exam --paper paper.md --reference reference.md \
  --answers answers/ --name quiz1 --granularity half --note "units are required"
```

`--paper` is the question paper (txt, md, docx, text pdf or json). `--reference` takes the model answer and/or rubric as one combined file or several files; it may be left out. `--answers` is a folder with one file per student (or the output folder of `autograde ocr`), or one JSON file. The teacher's only inputs are `--granularity` (rubric, none, half, quarter), `--strictness` and a free-text `--note`. Results go to `runs/<name>/`: `schemes.md` (read this first), `marks.csv`, `students/<student>.md` (marks and feedback). `--schemes-only` stops after the schemes. Feedback is always written.

Open `runs/<name>/report.html` to read the samples (question, model answer, student answer with quoted evidence highlighted, our marks vs the teacher's, feedback; filter to answers that differ from the teacher). `run` and `judge` rebuild it automatically.

Outputs go to `runs/<name>/`: `report.html`, `results.jsonl` (marks, per-point verdicts, feedback, flags), `metrics.json`, `usage.json`. Interrupted runs resume where they stopped. Marking schemes are stored in `rubrics/<model>/<variant>/` (JSON, plus readable `<dataset>.md` from `autograde rubrics-md`).

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
| `src/autograde/prompts/` | Every prompt, as markdown, grouped by stage (`rubric/`, `grade/`, `feedback/`, `language/` for anything specific to a language other than English, `intake/`, `ocr/`, `checks/`, `eval/`); a prompt is found by file name |
| `configs/` | `default.yaml`, `exam.yaml`, `poc.yaml`, `models/`; one-off experiment configs are in `configs/experiments/<group>/` |
| `scripts/` | Shell chains that ran sets of experiments (A/B tests, translated sets, OCR) |
| `tools/` | Standalone OCR scripts (`tools/ocr/`) and the code-sandbox interpreter (`tools/sandbox/`) |
| `rubrics/` | Every stored marking scheme, by model and strictness |
| `src/autograde/cli/` | Commands, one module per group (runs, evals, rubrics, pages) |
| `src/autograde/ocr/` | OCR track: simulated noise, image transcription (see its README) |
| `src/autograde/evaluation/` | Mark metrics, feedback judge |
| `src/autograde/viewer/` | `report.html` template and builder |

Data splits: a question goes to `dev` or `test` by a hash of its id, so no question appears in both. Tune on `dev`; run `test` rarely.

## Experiment workflow (every test against the teacher's marks)

`autograde run ... --variant NAME --note "what changed"` does five things in order:
grades the sample, scores it against the teacher's marks, appends a line to `experiments/log.jsonl`,
rebuilds `experiments/RESULTS.md` (all runs, with change against the baseline and the previous run
on the same sample), then commits the code and tags it.

- Commit subject carries the scores: `exp(v1): error 0.150 | bias -0.04 | r 0.85 | qwk 0.75 | $0.60 [...]`.
- Tag `exp-<variant>-<run>` holds the full message: `git show exp-v1-dk_s1_v1`.
- List everything tried: `autograde history` (same as `git tag -n1 -l "exp-*"`).
- Fall back: `git checkout exp-<variant>-<run>`. Marking schemes in `rubrics/` are committed,
  so the exact schemes come back with the code.
- Nothing is pushed. Push when you choose: `git push --follow-tags`.
- `--no-commit` skips the git step for throwaway runs.

Compare designs on the **same sample** (same dataset, split, `-n`, `--seed`). Tune on one seed and
confirm on another so a gain is not just fitting the tuning sample.

## Switches (configs/default.yaml, `pipeline:`)

| Switch | Default | Meaning |
|---|---|---|
| `read_first` | true | A first pass reads the answer alone (no model answer, no scheme), then marking uses that reading |
| `evidence_policy` | flag | `strict`: credit with an unfound quote is removed. `flag`: kept and reported |
| `policy` | essence | `essence`: judge the central idea, model answer is one example. `literal`: original wording |
| `rubric_variant` | sized | Folder name for a different marking-scheme source, so schemes can be compared |
| `feedback_variant` | standard | `standard`, `hints` (guide, do not give the idea), `critique` (draft then review), `formal` |
| `feedback_n` | 1 | Write this many feedback drafts; code checks drop bad ones and the model picks the best |
| `votes` | 1 | Mark this many times and take the majority per point. Same-model votes were identical in tests, so leave at 1 |
| `second_model` | none | A cheaper model also marks; a gap over `disagree_gap` adds the flag `models_disagree` |

Marking always applies a form check: scrambled text earns 0, a bare list of terms (where an explanation was asked) is capped at half, and instructions inside a student answer are ignored.

`configs/experiments/compare/v0_citations.yaml` switches all three off to reproduce the first design.

## Tests beyond the teacher's marks

| Command | What it checks |
|---|---|
| `autograde stress --dataset D --mode pipeline\|baseline --name N` | Answers built so the right outcome is known (shuffled words, keyword lists, off-topic, confident wrong, pasted model answer, injected instructions). Needs no human labels |
| `autograde revision --name R [--sample N]` | A simulated student rewrites the answer using only the feedback; the grader marks the rewrite. Compared with a no-feedback rewrite |
| `autograde transfer --name R` | The same student answers a different question on the same idea, so memorised answers do not count |
| `autograde run ... --perturb-model mask30\|short50` then `autograde sensitivity --a A --b B` | How far marks move when the model answer is blanked or shortened |
| `autograde refeedback --name R --new-name N --feedback hints --variant V` | New feedback on a finished run; marks stay identical |
| `autograde votes --name R` | Vote spread and, with `second_model`, how well disagreement points at errors |
| `autograde compare --run NAME=LABEL\|SHORT\|DESCRIPTION ...` | One page, one tab per method, the same answers in each |

`autograde download --engsaf` fetches EngSAF (benchmark only: it ignores the dev/test split and is never tuned on).

## Framework choice

No agent framework (LangGraph, Agents SDK). The flow is a fixed sequence of model calls with code checks between them, so plain functions are simpler to test and debug. Revisit if the flow needs branching or tool use (for example a calculator in stage 2).

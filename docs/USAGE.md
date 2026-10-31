# Usage reference

This page lists every command, flag and switch. For a first run, use the quick start in the
[README](../README.md). To understand the code, read the [codebase guide](GUIDE.md).

## 1. Set up

You need Python 3.11 or newer and [uv](https://docs.astral.sh/uv/).

```bash
uv sync --all-extras          # runtime, web app, file readers, sandbox and dev tools
uv run pytest                 # optional: the tests run offline
```

For a real model, copy `.env.example` to `.env` and add `OPENROUTER_API_KEY`. Keys are never put in
a config file.

## 2. Mark an exam: `autograde exam`

```bash
autograde --config configs/exam.yaml exam \
  --paper paper.docx --reference key.docx --answers answers/ \
  --name quiz1 --strictness moderate --note "units are required"
```

Put `--config` **before** the command name, and keep the `.yaml` ending. Use `configs/mock.yaml` to
try the command offline.

### Inputs

| Flag | Meaning |
|---|---|
| `--paper` | The question paper: txt, md, docx, text PDF or json. Required |
| `--reference` | The model answers and/or rubric, in one file or several. Optional |
| `--answers` | A folder with one file per student (or the output of `autograde scan`), or one json file. Required |
| `--name` | A name for this run. Results go to `output/runs/<name>/`. Required |
| `--max-mark` | The marks for a single question when the paper does not print them |

### Teacher controls

| Flag | Meaning |
|---|---|
| `--strictness` | `lenient`, `moderate` or `strict`: how tightly each point is judged |
| `--granularity` | How part marks work, overriding the rubric: `rubric` (its own levels), `stated` (only the levels it names, otherwise all or nothing), `none`, `half` or `quarter` |
| `--mark-step` | Marks come in multiples of this number: 0.5 allows 1.5 out of 2, and 0.2 allows 1.8 |
| `--note` | Free text for the marker, for example `"units are required"` |
| `--question-note ID=TEXT` | A note for one question only. Repeat the flag for more |
| `--no-follow-through` | Do not credit a later part that is right on the student's own earlier result |
| `--working-required` | A numerical answer with no formula or working earns no marks |
| `--count-best N` | Only the best N questions count towards the total. By default this is read from the paper |
| `--struck-out STUDENT=Q` | A question the student struck out. It is not marked |
| `--ignore-rubric-rules` | Do not read exam-wide rules from the paper and the rubric |
| `--schemes-only` | Write the marking schemes and stop. Read `schemes.md` before you mark |

Feedback is always written for answers that lost marks.

### Code questions

| Flag | Meaning |
|---|---|
| `--code-exec` | Run tests on student code in the sandbox. If the teacher gave no tests, the model writes them, and only tests that the reference solution passes are kept |
| `--code-sandbox` | Where the code runs: `wasm` (the default, standard library only), `docker`, or `process` (only for code you trust) |

### Who wrote each sheet

| Flag | Meaning |
|---|---|
| `--directory` | A student list: the web app's database and/or CSV files with `student_id` and `name`. Each sheet is then matched to a student by the roll number and name written on it, and not by its file name |
| `--course-id` | With `--directory`: prefer the students enrolled in this course when matching names |
| `--identity-fixes` | A json file `{file name: student id}` for sheets a teacher matched by hand |
| `--allow-unresolved` | Mark the sheets that were identified and leave out the rest. By default, marking stops if any sheet cannot be matched |

### What you get

All files are in `output/runs/<name>/`:

| File | Contents |
|---|---|
| `schemes.md` | The marking scheme for each question. **Read this first** |
| `marks.csv` | One row per student |
| `students/<student>.md` | Each student's marks and feedback |
| `results.jsonl` | Every verdict, quote, flag and piece of feedback |
| `report.html` | A page for reading the results (see section 5) |
| `usage.json` | Tokens used |

An interrupted run resumes where it stopped.

## 3. Read handwritten sheets: `autograde scan`

```bash
autograde --config configs/exam.yaml scan sheets/ --out answers/ --paper paper.docx
```

This reads photographed sheets into one text file per student, which you can pass to `exam`.

**You choose the readers.** The `ocr:` block of the config holds the main reader (`reader`) and
the fallbacks (`fallbacks`), which are tried in order. A reader is passed over when it fails, reads
nothing, marks more than 25% of the words as uncertain, or repeats one word. If none is clean, the
least doubtful read is kept and marked as degraded in `scan.json`. The README section "Reading
handwriting" has the diagram, the default chain and the keys and costs.

`--provider` and `--model` replace the main reader for one run. The fallbacks from the config still
apply after it.

**Optional Indian-script route.** Add this to the `ocr:` block to re-read every page that looks
Indian-script (30% or more of its letters), even when the main reader was clean:

```yaml
  routes:
    - {when: indic, reader: {provider: bodhan, model: "<model name from the Bodhan console>"}}
```

Check the text before marking, because reading handwriting is an AI step and it can make mistakes.

## 4. Mark one answer again: `autograde recheck`

```bash
autograde --config configs/exam.yaml recheck --name quiz1 --student S01 --question 2b \
  --note "accept either method" --out proposal.json
```

This marks one answer again with a note from the teacher. It only writes a proposal. Nothing in the
finished run changes until a person accepts it.

## 5. Read a run: `report.html`

`output/runs/<name>/report.html` shows every answer: the question, the model answer, the student's
answer with the quoted evidence highlighted, the marks, and the feedback. When a dataset run has
teacher marks, it also shows ours against the teacher's, and it can filter to the answers that
differ. `autograde view --name <run>` rebuilds the page.

## 6. Measure the grader on public datasets

These commands are for developers who want to know how accurate the grader is. They need the public
datasets in `data/raw/` (see [DATASETS.md](DATASETS.md)).

```bash
uv run autograde download                      # fetch the openly licensed datasets
autograde run --dataset digiklausur --split dev -n 24 --mode baseline --name dk_baseline
autograde run --dataset digiklausur --split dev -n 24 --mode pipeline --name dk_pipeline
autograde judge --name dk_pipeline             # score the feedback with a second model
autograde report --name dk_pipeline            # print the accuracy figures
```

Questions are split between `dev` and `test` by a hash of the question's id, so no question is in
both. Tune on `dev`, and run `test` rarely. Always compare designs on the **same sample** (same
dataset, split, `-n` and `--seed`).

### The experiment log

Each `autograde run` adds one line to `experiments/log.jsonl` (the settings, a fingerprint of the
prompts and the score against the teacher) and rebuilds `experiments/RESULTS.md`. Use
`autograde history` to list what has been tried. Add `--commit` to also make a git commit and tag
for the run. This is off by default, because it runs `git add -A`.

### Pipeline switches

These are the `pipeline:` settings in `configs/default.yaml`.

| Switch | Default | Meaning |
|---|---|---|
| `read_first` | true | A first pass reads the answer alone, then marking uses that reading |
| `evidence_policy` | flag | `strict` removes credit whose quote is not found. `flag` keeps the credit and reports it |
| `policy` | essence | `essence` judges the central idea, and the model answer is only one example. `literal` follows the original wording |
| `rubric_variant` | sized | The name of the scheme source, so different schemes can be compared |
| `feedback_variant` | standard | `standard`, `hints` (guide, but do not give the idea), `critique` (draft, then review) or `formal` |
| `feedback_n` | 1 | Write this many drafts. Code removes bad ones and the model picks the best |
| `votes` | 1 | Mark this many times and take the majority per point. In tests, votes from one model were identical, so leave it at 1 |
| `second_model` | none | A cheaper model also marks. A gap above `disagree_gap` adds the flag `models_disagree` |

Marking always applies a form check. Scrambled text earns 0, a bare list of terms (when an
explanation was asked for) is capped at half marks, and instructions written inside a student answer
are ignored.

### Tests beyond the teacher's marks

| Command | What it checks |
|---|---|
| `autograde stress --dataset D --mode pipeline --name N` | Answers built so that the right outcome is known: shuffled words, keyword lists, off-topic text, confident wrong answers, pasted model answers and injected instructions. It needs no human marks |
| `autograde revision --name R` | A simulated student rewrites an answer using only the feedback, and the grader marks the rewrite. This is compared with a rewrite made without feedback |
| `autograde transfer --name R` | The same simulated student answers a different question on the same idea, so memorised answers do not count |
| `autograde sensitivity --a A --b B` | How far marks move between two runs, for example when the model answer was blanked or shortened (`--perturb-model`) |
| `autograde refeedback --name R --new-name N --feedback hints` | Writes new feedback for a finished run. The marks stay identical |
| `autograde votes --name R` | How much votes differ, and how well disagreement points at errors |
| `autograde compare --run NAME=LABEL\|SHORT\|DESCRIPTION ...` | One page with a tab per method, showing the same answers in each |

`autograde download --engsaf` fetches EngSAF. It is for benchmarking only: it ignores the dev/test
split and is never used for tuning.

## 7. Why there is no agent framework

The flow is a fixed series of AI calls with code checks between them, so plain functions are easier
to test and debug than an agent framework. This choice can be revisited if the flow ever needs
branching or tools, for example a calculator.

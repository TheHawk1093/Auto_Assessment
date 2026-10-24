# Auto Assessment — Project Doc

Living doc. One fact per line, update on every decision. Coding/tooling rules live in CLAUDE.md. Readable plan: `artifacts/Planning_and_Ideation/project_roadmap.html`. Live status: `artifacts/Project_Tracker/tracker.html` (edit only `tracker.json` there, then run `python artifacts/Project_Tracker/build.py`; result numbers come from `runs/` automatically).

## 1. Goal
Grade a full answer sheet against model answers and a marking scheme, fully automatically, with feedback a student can learn from.

## 2. I/O Contract
**Inputs (per exam):** question paper, student answer sheets, model answer per question, marking scheme per question (optional; AI-generated if absent).
**Outputs (per student):** marks per question + total; feedback per question (what was right, which scheme points were missed and why, what to do next).

## 3. Success Metrics
- **Marks:** same-mark rate and average error vs. teacher marks on held-out questions; strict/lenient bias; compared with a one-prompt baseline.
- **Feedback:** automatic 5-question check by a different-provider model (specific, names missed point, explains why, next step, correct); SAF teacher feedback as reference.
- **Scheme quality:** model answer gets full marks, blank answer gets zero, marks sum to total.
- Targets are set after the first baseline run.

## 4. Pipeline
1. Read exam → per-question pieces (code)
2. Marking scheme: use given, else AI writes once per question, auto-tested (AI)
3. Mark each answer per scheme point with quoted evidence (AI)
4. Check: quotes exist, limits, total added by code, one retry (code)
5. Write feedback from checked marking (AI)
6. Report per student (code)

## 5. Principles
- Fully automatic at run time. No human review step. Humans only read samples during development; no hand-labelling.
- Code does arithmetic and checks; AI does judgement.
- Every mark ties to a scheme point and a quote from the answer.
- Start simple; add a component only if it measurably helps.
- Model is one config line; feedback judge uses a different provider.

## 6. Scope
- **In:** typed answers, STEM, a few domains at a time.
- **Out for now:** handwriting (stage 3), drawn diagrams, plagiarism, curving.

## 7. Stages
| Stage | Domains | Data | Status |
|---|---|---|---|
| 1 | CS / networking short answers | DigiKlausur, SAF, Mohler (tune on dev); EngSAF (benchmark only, never tuned) | in progress: design v6 hardened with stress tests; held-out test split not yet run |
| 2 | Maths, physics, chemistry with working | SciBench/UGMathBench questions + generated practice sheets, ProcessBench, PRM800K, RiceChem (if access) | not started |
| 3 | Handwriting, circuits | EDU-CIRCUIT-HW | later |
| 4 | Other fields | none identified | optional |

Dataset detail: [DATASETS.md](DATASETS.md).

## 8. Decisions
| # | Decision | Status |
|---|----------|--------|
| 1 | Typed text first; handwriting later | decided |
| 2 | Fully automatic; no human-in-loop at run time | decided |
| 3 | No hand annotation; evaluate with dataset marks + generated sheets + AI judge | decided |
| 4 | One call per question; code sums marks; separate feedback call | decided (revisit on data) |
| 4b | No agent framework (LangGraph / Agents SDK): fixed call sequence + code checks, plain Python; revisit only if we need loops, branching on tools, or persistence | decided |
| 8 | Final project / package name (`autograde` is a working name; PyPI already has an unrelated `autograde`) | open |
| 4c | Early testing via Claude Code CLI backend; API backend ready but untested (no key yet) | decided |
| 5 | No fine-tuning, no examples initially | decided (revisit on data) |
| 9 | Verdicts priced in code (partial = 0.9 of a point), scheme sized to the model answer | decided (tuned on dev) |
| 10 | Same-model voting: no effect (marks identical across 3 votes). Use a cheaper second model as a review flag instead | decided |
| 11 | Form gate: scrambled text earns 0, bare keyword lists capped at half, student text treated as data | decided (found by stress test) |
| 12 | EngSAF is benchmark-only: results reported, never tuned on | decided |
| 13 | Default feedback style (standard, critique, hints, formal, best-of-3) | open: critique scored best on the judge; owner to read and choose |
| 6 | Model/provider and budget | pending (owner) |
| 7 | Output format (file per student vs table) | open |

## 9. Changelog
- 2026-10-09 — Project doc created; dataset survey; DATASETS.md.
- 2026-10-11 — Replaced first planning page (too technical) with simpler staged roadmap; made fully-automatic and no-annotation explicit; rewrote pipeline and stages.
- 2026-10-13 — Stage-1 data downloaded (data/raw); autograde package v0: loaders, rubric maker + self-test, grader + checks, feedback writer, baseline, metrics, feedback judge, CLI, 26 tests.
- 2026-10-15 — Added visual tracker (artifacts/Project_Tracker/tracker.html).
- 2026-10-15 — Tracker split into tracker.json + template + build.py so updates are a small JSON edit; added readable report.html per run; CLAUDE.md added.
- 2026-10-16 — Experiment tracking (log, tags per run); design v2b: read-first, code-priced verdicts, sized schemes; beats baseline on all three dev sets.
- 2026-10-17 — Feedback now explains why; model/effort sweep (sonnet default best value); revision test; hints/critique feedback; side-by-side comparison page.
- 2026-10-18 — Stress test (answers with a known right outcome) found v2b too easy to fool; form gate and injection guard added (stress 0.67 to 0.86); transfer test; formal and best-of-3 feedback; model-answer masking; EngSAF added as a benchmark-only dataset; second-model review flag. Same-model voting found useless.
- 2026-10-25 — Cleanup: commands split into `cli/` modules; all rubrics moved to `rubrics/` (JSON plus readable markdown); rejected prompt removed. Rubrics can set their own policy and partial weight (RiceChem official: balanced, 0.5; "implied is not stated" added to moderate). OCR option added to the reader (`run --ocr light|medium|heavy`). Haiku-only proof of concept (`configs/poc.yaml`, `autograde poc`): pipeline beats baseline on 4 of 5 datasets at 8 answers each; EngSAF is the exception.

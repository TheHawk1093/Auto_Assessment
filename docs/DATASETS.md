# Dataset Card — Auto Assessment

Catalog of candidate datasets, how each is used, and which to develop vs. test on. Source of truth for data decisions; PROJECT.md links here.
Status: facts taken from paper abstracts, READMEs and dataset cards (2026-10-09). Anything marked **(unverified)** must be checked before use. Licenses must be re-checked before redistribution.

## 1. Rating Scheme
Each criterion 1–5 (5 = best for us).

| Criterion | Meaning |
|---|---|
| **Fit** | Closeness to target task: STEM, full answers, rubric-linked marks, feedback |
| **Truth** | Reliability of human labels (multi-rater, per-criterion, expert) |
| **Access** | Ease/legality of getting the data (5 = open download) |
| **Prep** | Preparation effort (5 = almost none) |

**Role**
- **Dev** — iterate freely: prompts, rubric format, agent design, ablations.
- **Test** — held-out: run only at milestones, never tune on it.
- **Baseline** — calibration against published results only.
- **Pool** — source of questions/reference solutions for synthetic data.

## 2. Categories
| Cat | Type | What it gives us | Datasets |
|---|---|---|---|
| A | Rubric-graded real student responses | Closest to the target | RiceChem, EDU-CIRCUIT-HW |
| B | Scored real responses with feedback / reference answers | Marks + feedback style | SAF, DigiKlausur |
| C | Short-answer scoring baselines | Literature comparison | Mohler, SciEntsBank/Beetle, ASAP-SAS |
| D | Step-labelled solutions | Error localisation, partial credit (math) | PRM800K, ProcessBench |
| E | Student errors with misconception notes | Misconception-aware feedback | MathDial, Eedi |
| F | Question + reference-solution pools | Raw material for synthetic sheets | SciBench, UGMathBench, JEEBench, MIT/Columbia STEM |
| G | Watch list | Not usable yet | ALICE-LP-1.0, handwritten college math |

## 3. Dataset Entries

### A. Rubric-graded real student responses
**RiceChem** — [paper](https://arxiv.org/abs/2404.14316) · [repo](https://github.com/luffycodes/Automated-Long-Answer-Grading)
- Domain: college chemistry. 1,264 long answers (avg ~120 words), 4 exam questions, 27 binary rubric items, 8,392 criterion labels.
- Labels: per-criterion human labels. Criterion weights were inferred by regression, not given.
- Access: request via Google form; no license stated. Not in repo.
- Prep: map rubric items → our rubric schema; reconstruct marks from weights; question text/reference answer may need to be added.
- Limits: only 4 questions → overfits easily; use for test, not dev.

**EDU-CIRCUIT-HW** — [paper](https://arxiv.org/abs/2602.00095) · [repo](https://github.com/gt-learning-innovation/CIRCUIT_EDU_HW_ACL) · [data DOI](https://doi.org/10.35090/gatech/81252)
- Domain: circuit analysis (Georgia Tech, Spring 2025). 1,334 handwritten solutions, 29 students, 62 questions.
- Files: handwritten PNGs, grades, rubric outputs, expert transcripts for the 513-sample observation set only (821-sample test set has no rectified transcripts).
- Access: code Apache-2.0; dataset licence not stated; problem statements withheld (copyright) — contact authors.
- Prep: images need OCR/VLM transcription for typed-text pipeline (or use the 513 verified transcripts); obtain problem statements; align rubrics.
- Limits: handwriting + missing problem text; best as stage-2 handwriting benchmark.

### B. Scored real responses with feedback / reference answers
**SAF (Short Answer Feedback)** — [paper](https://aclanthology.org/2022.acl-long.587/) · [repo](https://github.com/SebOchs/SAF) · HF org `Short-Answer-Feedback`
- Domain: communication networks (English, university) + German micro-job. 4,519 answers; score + elaborated feedback + reference answer.
- Access: repo MIT; dataset licence **(unverified)**. Question counts conflict across papers (22 vs 26 English).
- Prep: map to our schema; derive rubric from published scoring guidelines (authors released rubrics, per search snippet — **unverified**).
- Use: only dataset with human feedback text → reference for feedback style and a feedback-quality judge.
- Limits: short answers; feedback is brief.

**DigiKlausur ASAG** — [repo](https://github.com/DigiKlausur/ASAG-Dataset)
- Domain: neural networks exam, grad students. 646 answers (38 students × 17 questions). Reference answers, 0/1/2 scores, per-student exam notebooks.
- Access: MPL-2.0, open.
- Prep: write rubrics (17 questions — cheap); parse notebooks into full sheets.
- Limits: single grader, coarse 0–2 scale, no feedback. Good end-to-end smoke test.

### C. Short-answer scoring baselines
| Dataset | Domain / size | Labels | Access |
|---|---|---|---|
| [Mohler 2011](https://aclanthology.org/P11-1076/) | CS data structures, ~2.2k answers, ~80 q | 0–5 by 2 graders; reference answers | ACL zip; licence unverified |
| SciEntsBank / Beetle (SemEval-2013 T7) | Science ~10k / electricity ~3k, 1–2 sentence | 5-way correctness; reference answers | HF `Spal09/sem_eval_2013_task_7` (community mirror) |
| [ASAP-SAS](https://www.kaggle.com/c/asap-sas/data) | Science/biology/ELA, 17k train | 0–3 | Kaggle; check rules |

Prep: low per dataset but low value — answers too short, no rubric, no feedback. Use only to compare with published numbers.

### D. Step-labelled solutions (math)
**PRM800K** — [repo](https://github.com/openai/prm800k) (MIT)
- MATH problems, reference solutions, 800k step labels (-1/0/+1) on LLM solutions. JSONL, Git LFS.
- Prep: convert step labels to rubric-style marks; large download.
- Use: validate error localisation and partial credit in math.

**ProcessBench** — [HF](https://huggingface.co/datasets/Qwen/ProcessBench) (Apache-2.0)
- ~3.4k solutions (GSM8K 400, MATH/OlympiadBench/Omni-MATH ~1k each); `steps`, `final_answer_correct`, `label` = first erroneous step.
- Prep: minimal. Small, clean, expert-labelled.
- Limits: model-written solutions, not student style; math only.

### E. Student errors with misconception notes
**MathDial** — [repo](https://github.com/eth-nlped/mathdial) (CC BY-SA 4.0 — share-alike applies to derivatives)
- 2,861 tutoring dialogues on GSM8K problems; fields: `question`, `ground_truth`, `student_incorrect_solution`, `teacher_described_confusion`.
- Simulated (LLM) students, not real. Use to test misconception-aware feedback.

**Eedi / MIME** — [overview](https://eedi.com/blog/from-wrong-answers-to-real-insights-how-we-used-a-kaggle-challenge-to-map-student-misconceptions)
- Real K-12 MCQ answers with short explanations, misconception labels. Licence **(unverified)**. Low fit (MCQ, school math).

### F. Question + reference-solution pools
| Dataset | Domain / size | Provides | Licence | Caveat |
|---|---|---|---|---|
| [SciBench](https://github.com/mandyyyyii/scibench) (HF `xw27/scibench`) | College physics, chemistry, math (textbooks) | Problems, answers; worked solutions **(unverified)** | MIT | Many numeric-answer items |
| [UGMathBench](https://huggingface.co/datasets/UGMathBench/ugmathbench) | Undergrad math, ~5k, 16 subjects | Problems, final answers, 3 randomised versions | GPL-3.0 | No worked solutions confirmed; copyleft |
| [JEEBench](https://alphaxiv.org/benchmarks/iit-delhi/jeebench) | IIT JEE Adv. P/C/M, 515 | Problems, final answers | **(unverified)** | Mostly MCQ/numeric |
| [MIT/Columbia STEM](https://ojs.aaai.org/index.php/AAAI/article/view/27091) | 27 university courses (chem, physics, ME, EE) | Problem sets/exams | **(unverified)** | Download unconfirmed |

Prep for all: generate rubric (LLM + human review) and synthetic student answers (see §5).

### G. Watch list
- [ALICE-LP-1.0](https://edutec.science/bea-2026-shared-task/) — German school STEM, rubric levels 0–2. Wrong language for now.
- [Handwritten college math](https://arxiv.org/abs/2603.00895) — release not confirmed.

## 4. Ratings and Roles
| Dataset | Fit | Truth | Access | Prep | Role | Why |
|---|---|---|---|---|---|---|
| RiceChem | 5 | 5 | 2 | 4 | **Test (primary)** | Per-criterion human labels on STEM long answers; request access now |
| EDU-CIRCUIT-HW | 4 | 4 | 3 | 2 | **Test (stage 2)** | Real STEM sheets with rubrics; typed subset via 513 transcripts, handwriting later |
| SAF | 3 | 4 | 5 | 3 | **Test + Dev (feedback)** | Only human feedback text; calibrates feedback-quality judge |
| DigiKlausur | 3 | 3 | 5 | 2 | **Dev (smoke test)** | Open, full-exam-shaped, small enough to hand-write rubrics |
| SciBench | 3 | – | 5 | 4 | **Dev (primary pool)** | STEM question pool → synthetic sheets with known marks |
| ProcessBench | 2 | 5 | 5 | 4 | **Test (component)** | Verifies error localisation in verification stage |
| PRM800K | 2 | 4 | 5 | 3 | **Dev (component)** | Large step-labelled set for partial-credit logic in math |
| MathDial | 2 | 2 | 5 | 3 | **Dev (feedback)** | Student errors with misconception text |
| UGMathBench | 2 | – | 5 | 3 | Pool (secondary) | Extra undergrad math questions; GPL-3.0 caution |
| Mohler | 2 | 3 | 4 | 2 | Baseline | Literature comparison only |
| JEEBench | 2 | – | 3 | 3 | Pool (optional) | India-exam relevance; MCQ-heavy |
| SciEntsBank/Beetle, ASAP-SAS | 1 | 3 | 4 | 1 | Baseline | Too short, no rubric/feedback |
| Eedi/MIME | 1 | 3 | 3 | 2 | Skip | MCQ, school-level |
| MIT/Columbia STEM | ? | – | ? | ? | Verify | Could be best pool if downloadable |

## 5. Recommended Split
> Superseded in part by the stage plan in PROJECT.md §7 (stage 1: DigiKlausur, SAF, Mohler; RiceChem is a bonus, not a dependency). Principle unchanged: tune on one part, run once on held-out questions.

**Dev (iterate freely)**
1. DigiKlausur — end-to-end smoke test, rubrics hand-written.
2. Synthetic set from SciBench (+ UGMathBench) — rubric generated and reviewed; student answers LLM-written with *logged injected errors*; true marks derived from the error log, not an LLM re-grade.
3. PRM800K / MathDial subsets — math partial credit and misconception feedback.

**Test (frozen; run at milestones)**
1. RiceChem — rubric-level agreement.
2. SAF test split — feedback quality vs. human feedback.
3. ProcessBench — error-localisation component.
4. EDU-CIRCUIT-HW — stage 2 (handwriting).

**Rules**
- Never tune prompts/rubrics on Test data. Split by *question*, not by answer, to avoid leakage.
- Keep a small hand-checked slice of synthetic data (~10%) to confirm the injected-error labels are right.
- Owner's manual review is the final judge of feedback usefulness; automated numbers are supporting evidence.

## 6. Action Items
- [ ] Submit RiceChem access request.
- [ ] Download DigiKlausur, SAF, ProcessBench, SciBench (all open).
- [ ] Verify licences marked **(unverified)**.
- [ ] Check MIT/Columbia STEM availability.
- [ ] Contact EDU-CIRCUIT-HW authors for problem statements.

## 5. Downloaded samples for per-category prompts (`autograde download --samples`, about 9 MB, in data/raw)

| Category | Folder | What is there | Marks available |
|---|---|---|---|
| Maths, step-wise solutions | processbench | gsm8k (400) and math (1000) model-written solutions split into steps | First wrong step (label -1 = all correct), final-answer correct |
| Physics, chemistry (numeric) | scibench | fund (71 physics) and atkins (105 physical chemistry) problems, with worked solutions for a few | Final numeric answer and unit |
| School science short answers | scientsbank | SemEval-2013 test split, 23,656 answers, 5-way labels, reference answers | correct / partially correct / contradictory / irrelevant / non-domain |
| Maths misconceptions | mathdial | 599 tutoring dialogues with the student's wrong solution and the teacher's note on the confusion | Misconception text, no marks |
| Essays and language | aes2 | 958 persuasive essays | Holistic score 1 to 6 (CC BY-NC) |
| Essays with examiner feedback | ielts | 189 IELTS task-2 essays with a chosen and a rejected feedback text | Preference pairs, no score |

Two more were wrongly marked "needs sign-up" at first and are now fetched:

| Category | Folder | What is there | Marks available |
|---|---|---|---|
| Short answers with rubric text | asap_sas | 763 answers from the 10 ASAP-SAS prompts (public HF mirror `nlpatunt/D_ASAP-SAS`; the prompt column holds the question and its rubric) | Score 0 to 3 (two graders) |
| Handwritten circuit analysis | circuit_hw (`download --circuit`) | 62 per-question rubrics, TA labels for 232 answers, 12 handwritten pages of one student, read out of the 9 GB archive by range requests | Per-criterion deductions |

Problem statements for EDU-CIRCUIT-HW are withheld by the authors (textbook copyright), so questions are known only by id. The full archive (9 GB, 3,765 page images) was not downloaded. Not downloaded: Eedi (sign-up). Loaders are not written yet; these folders are raw files.


### Harder sets added for the solid-rubric tests (`download --samples`)

| Category | Folder | What is there | Marks available |
|---|---|---|---|
| Olympiad proofs | imo_grading | IMO-GradingBench (Google DeepMind, CC BY 4.0, HF mirror `Hwilner/imo-gradingbench`): 1,000 model-written proofs to 30 olympiad problems, with grading guidelines and the human grader's note | Score 0 to 7 (300 zeros, 300 sevens, 400 in between) |
| Maths, subtle errors | processbench_hard | The olympiadbench (1,000) and omnimath (1,000) parts of ProcessBench | Whole-solution correct or not |

Known defect in ASAP-SAS: the prompt of set 4 holds two different questions (pandas and koalas, and the word "invasive"), and students answered one or the other, so no scheme can fit all its answers. Results are also reported without set 4. Loaders: `load_imo_grading`, `load_processbench_hard` in `datasets/extra.py`; both are measurement only.

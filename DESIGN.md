# Design choices and experiments

One place for what we built, why, and what the tests showed. Numbers come from `experiments/log.jsonl` (every run is logged, committed and tagged). Error means the average gap to the teacher's mark as a share of the question total (lower is better). Bias below 0 means stricter than the teacher.

## 1. Goal

Given a question, a model answer, a rubric and a student answer, mark the answer the way the teacher would, and write feedback that helps the student learn. No human step at run time. Teacher marks in the datasets are the ground truth we tune against. We tune prompts and settings, not model weights.

Rules we keep:
- Tune on dev questions only. Test splits are for one final report.
- EngSAF and RiceChem are benchmark only: never tuned on.
- No agent framework. Code does arithmetic and checks, the model does judgement.
- Every ground-truth run is committed and tagged locally. Nothing is pushed.

## 2. The pipeline and why each stage exists

| Stage | What it does | Why |
|---|---|---|
| Marking scheme | One short list of points with marks, written once per question and stored in `rubrics/` | A fixed scheme makes marks repeatable and lets us price verdicts in code |
| Read first | The answer is read alone (gist, ideas, problems, form) before marking | The marker is not pulled towards the model answer's wording; helps garbled answers and formulas |
| Mark per point | Verdict (met, partial, not met) plus an exact quote, for each point | A verdict is easier to get right than a number, and the quote can be checked |
| Price in code | met is full marks, partial is weight times full marks, not met is 0 | Removes the model's arithmetic noise; partial value is one setting |
| Form gate | Scrambled answers get 0; a bare keyword list is capped at half, only if the question asks to explain | Catches answers that look right point by point but are not answers |
| Quote check | Credit whose quote is not in the answer is flagged | Catches invented evidence |
| Feedback | One call, written from the checked marking | Feedback must agree with the marks |

## 3. Design choices, with evidence

**Read first plus essence marking.** Read-first alone improved DigiKlausur (0.200 to 0.174) and SAF (0.112 to 0.081) but made Mohler slightly worse (0.225 to 0.252). Alone it was not enough.

**Price verdicts in code with partial = 0.9 (v2a).** The biggest single gain: DigiKlausur 0.098, SAF 0.057, Mohler 0.187. The model's own marks were too harsh; verdicts plus a price are steadier.

**Sized marking schemes (v2b).** Points sized to the model answer (one point per idea) beat free-form schemes: DigiKlausur 0.098 and 0.069, SAF 0.060, Mohler 0.155. A stricter variant (v3, "sized2") was worse (DigiKlausur 0.127, Mohler 0.192) and was removed.

**Model choice.** On the same 24 DigiKlausur answers: Haiku 0.106 ($0.10), Sonnet low effort 0.071 ($1.12), Sonnet high effort 0.110 ($1.23), Opus medium 0.089 ($2.90). More effort did not help. Sonnet was the default for the big runs, Haiku is used for the cheap proof of concept and tuning.

**Voting does not help.** Three markings by the same model changed nothing (0.069 either way) at about 5 times the cost. Extra calls from one model repeat its own errors. A cheaper second model as a "markers disagree" flag works but is an optional extra, off by default.

**Stress test and the form gate.** Answers with a known right outcome (a pasted model answer, scrambled text, keyword lists, off-topic, instructions hidden in the answer) showed the first design could be fooled (pass rate 0.667). Adding the form gate and an instruction guard raised it to 0.861. The first gate version capped genuine lists on SAF (error 0.060 to 0.106), fixed by letting short answers include lists (back to 0.060). A later Haiku misread of a requested list as a keyword list led to a second guard: the cap applies only if the question asks to explain, describe, justify and similar.

**Sensitivity to the model answer.** Masking 30% of the model answer and keeping only the first half of it both change marks; the shortened version raised error to 0.179. The marks depend on the reference wording more than we want.

**Rubric strictness levels.** Rubrics written lenient, moderate or harsh make the grader mark accordingly (policy and partial value come from the rubric). On RiceChem (72 answers): lenient 0.190 (bias +0.181), moderate 0.149 (+0.052), harsh 0.174 (-0.142, best correlation 0.89). On the Haiku proof of concept (8 answers per set) marks moved in the right order on all five datasets, and feedback grew more critical with strictness (Mohler: 0.62, 1.5 and 1.75 improvements per answer). Rubrics are therefore an input the user can steer with.

**Partial credit depends on the teacher.** Re-pricing saved RiceChem verdicts at 0.5 instead of 0.9 gave error 0.132 and bias -0.010 (was 0.150 and +0.116). On the Haiku proof of concept the best value was about 1.0 on DigiKlausur, SAF, Mohler and EngSAF but 0.5 on RiceChem. So a rubric can now carry its own partial weight and policy. `autograde calibrate` fits it from marked answers (an extra; needs about 20 marked answers to trust).

## 4. Datasets

| Dataset | Questions | Marks | Role |
|---|---|---|---|
| DigiKlausur | 17 | 2 | tuning (dev) |
| SAF | 21 | 1 | tuning (dev) |
| Mohler | 81 | 5 | tuning (dev), longest answers of the three |
| EngSAF | 120 | 2 | benchmark only |
| RiceChem | Q1, Q2, Q4 | 8 | benchmark only; official rubric, criterion labels, derived reference answer |

Order of difficulty used for the proof of concept: DigiKlausur, SAF, Mohler, EngSAF, RiceChem. OCR comes after, first with simulated noise.

## 5. Results so far

Full tables: `experiments/RESULTS.md`.

**Baseline (one prompt, no scheme) against the pipeline, 24 answers:**

| Set | Baseline | Pipeline v2b |
|---|---|---|
| DigiKlausur (seed 0) | 0.217 | 0.069 |
| SAF | 0.112 | 0.060 |
| Mohler | 0.225 | 0.155 |

**RiceChem, 72 answers, never tuned on:** baseline 0.154; official rubric 0.150; generated rubric 0.158. The pipeline matches the baseline on accuracy there, at about 4 times the cost, and adds per-point verdicts and feedback. This is the main open weakness: vague claims get credit, wrong statements are not deducted, and partial credit was too generous.

**Haiku proof of concept, 8 answers per set, about 25 cents:** pipeline error against baseline: DigiKlausur 0.122 / 0.250, SAF 0.150 / 0.181, Mohler 0.287 / 0.312, EngSAF 0.269 / 0.188, RiceChem 0.094 / 0.133. The pipeline wins on four of five; EngSAF is the exception.

**Does the feedback help?** Simulated Haiku student rewrites the answer using only the feedback, the grader re-marks it, and a rewrite without feedback is the control. Gain with feedback against control: DigiKlausur +0.24 vs +0.11, SAF +0.68 vs +0.13, Mohler +0.49 vs +0.11, EngSAF +0.79 vs +0.19, RiceChem +0.31 vs +0.16. No answer got worse. Feedback copied 3 to 6% of the model answer's phrases, except Mohler at 19%. The student is a model, not a person, and the test measures mark gain, not learning.

## 6. Why Haiku under-marks

Seen by reading the answers marked below the teacher:
1. It reads the model answer too literally. "Never says X" is given as the reason for partial or not met even when the student states the idea in other words (Mohler: "the information in the address the pointer points to" scored 0 against "dereference", the teacher gave 4 of 5).
2. It splits credit into big all-or-nothing points, so one judgement removes most of a question.
3. A form-check misfire on a requested list (fixed, see section 3).
4. Teachers are often more lenient than the model answer suggests.

## 7. Feedback design

Styles tried: standard, hints, critique (draft then review, 2 times the cost), formal, brief, detailed, coach, best-of-3. Marks are the same for all of them; they differ in wording and cost. The user chose the formal register.

Current template (formal, the default):
1. What the question asks for (one sentence).
2. What was right, with the student's own words quoted and what the quote shows.
3. Only where marks were lost, one entry each, labelled **partly there** (stated but not to standard: quote it and give the key idea), **missed** (left out: explain the concept and why it matters) or **incorrect** (stated wrongly: quote it and give the correct concept).
4. One closing line on what to improve first, in terms of the concept.

Rules: only the parts that are needed appear; no invented mistakes when something was simply missing; feedback aims at learning the concept so it applies to another question (checked with the transfer test, which asks a new related question); full-mark answers get a short confirmation of what was right, built by code with no model call.

## 8. Token use by stage (Haiku, low effort, 15 answers)

| Stage | Calls per answer | Input tokens per call | Output tokens per call |
|---|---|---|---|
| Read | 1 | about 4,900 | about 800 |
| Mark | 1 | about 5,600 | about 870 |
| Feedback | 1 | about 5,300 | about 890 |

Roughly 16,000 input and 2,600 output tokens per answer in total, about one third each. Most of the input is the fixed prompt that the Claude CLI adds to every call, not our text, so the three stages cost about the same. Skipping feedback for full-mark answers removes one call in three for those answers. The direct API backend would avoid the CLI overhead (not tested).

## 9. Open problems

- Haiku literalness on Mohler and similar (section 6); being addressed by the grader prompt rounds in section 10.
- Deductions for wrong statements are not supported (RiceChem rubric asks for them).
- Marks shift with the model answer's wording.
- RiceChem Q3 excluded until deductions work.
- Held-out test split not yet run.
- Cost about 4 to 5 times the baseline.

## 10. Fix-the-misses loop (Haiku, marking only)

Dev only: DigiKlausur, SAF and Mohler, 20 answers each, seed 1, fixed across rounds. Each round: run, list the largest disagreements with the teacher, name the cause, change the grading prompt, re-run, keep the change only if error drops overall.

| Round | Change | DigiKlausur | SAF | Mohler | Decision |
|---|---|---|---|---|---|
| 0 | start (sized rubrics, essence policy) | 0.151 (bias +0.016) | 0.146 (+0.036) | 0.247 (-0.243) | baseline |
| 1 | grader prompt: plain-words ideas count; not met only if the idea is absent | 0.140 (+0.047) | 0.146 (+0.036) | 0.249 (-0.245) | kept (harmless, small gain on one set) |
| 2 | rubric writer: fewer, broader idea-points ("lean") | 0.266 (-0.222) | 0.119 (+0.083) | 0.278 (-0.248) | rejected: worse on two of three sets |
| 3 | atomic facts: model answer split into weighted single claims (code sets the marks), each judged against the student's separately read ideas | 0.128 (-0.041), r 0.88 | 0.158 (-0.024), r 0.77 | 0.216 (-0.182), r 0.72 | optional variant `atomic`; mean error of the three 0.178 to 0.167 |

What the loop showed:
- DigiKlausur and SAF are not under-marked at 20 answers (bias near zero). The under-marking is mainly Mohler: the teacher gives 0.8 to 1.0 of the marks to 17 of 20 answers, while Haiku gave about half.
- Prompt wording did not move Mohler. The Haiku-written scheme splits a one-sentence model answer into two or three narrow points, and an answer that gets one right loses the other. Merging points made it worse elsewhere, because fewer points make each judgement bigger.
- Partial value is not the lever on Mohler: the best fit was 0.8 and the error barely changed (0.26 to 0.27).
- Per the request to keep tuning short, the loop stopped after round 2. Next lever to try, on this same sample: another model (Sonnet) for the marker, which the earlier sweep suggests is more tolerant than Haiku at low effort.
- Mohler has repeated rows for the same student answer (the same id twice in a 20-answer sample); not yet looked into.

## 11. Atomic facts (round 3) and feedback on a different question

**Atomic facts.** The model answer is broken into single claims, each with a weight of 1 to 3, and code turns the weights into marks that add up exactly (`rubric_variant: atomic`). The student side was already broken into separate ideas by the read-first step. The marker then judges each fact against those ideas. Result on the same 3 dev samples: DigiKlausur and Mohler improved (Mohler bias -0.245 to -0.182, DigiKlausur correlation 0.79 to 0.88), SAF got slightly worse (0.146 to 0.158). Averaged over the three sets error fell from 0.178 to 0.167. With 20 answers per set this is a small, mixed gain, not a settled one. It stays an optional variant until it is checked on more answers.

**Does the feedback help on a different question?** Transfer test on DigiKlausur (17 answers, new related question on the same concept, same cached questions and control as before):

| Feedback | With feedback | Without (control) | Lift |
|---|---|---|---|
| hints | 0.832 | 0.482 | 0.350 |
| formal (old) | 0.846 | 0.482 | 0.363 |
| standard | 0.859 | 0.482 | 0.377 |
| critique | 0.875 | 0.482 | 0.393 |
| best of 3 | 0.868 | 0.482 | 0.385 |
| **formal (new template)** | **0.859** | 0.482 | **0.377** |

The new template matches the best of the old styles (within noise on 17 answers) while being structured and, for full-mark answers, free. Earlier numbers were taken from the saved runs.

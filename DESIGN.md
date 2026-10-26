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

## 12. Model comparison on 40 answers per set (marking only)

Same 40 dev answers per set (seed 1), sized rubrics, read-first on, no feedback. Each setup writes its own rubrics except the last row (Sonnet writes them once per question, Haiku marks).

| Setup | DigiKlausur | SAF | Mohler | Mean error | Cost for 120 answers |
|---|---|---|---|---|---|
| Haiku, low effort | 0.152 (r 0.78) | 0.135 (r 0.86) | 0.249 (bias -0.21, r 0.71) | 0.179 | $0.22 |
| Haiku, medium effort | 0.170 (r 0.65) | 0.127 (r 0.89) | 0.281 (bias -0.23, r 0.67) | 0.193 | $0.23 |
| Sonnet | 0.131 (r 0.80) | 0.128 (r 0.90) | 0.179 (bias -0.13, r 0.81) | 0.146 | $3.00 |
| Haiku medium + Sonnet-written rubrics | 0.162 (r 0.72) | 0.151 (r 0.84) | 0.215 (bias -0.14, r 0.70) | 0.176 | $0.25 + one-off rubric cost |

What it shows:
- Medium effort gave Haiku no gain over low (mean 0.193 against 0.179). More thinking does not fix what limits Haiku.
- Sonnet is clearly better on Mohler (0.179 against 0.249) and about equal on the shorter sets. It costs about 14 times more.
- Sonnet-written rubrics help Haiku on Mohler (0.281 to 0.215) and not elsewhere. The rubric is paid for once per question, not once per answer, so this is nearly free.
- The cost for the mixed row leaves out the Sonnet rubric cost, which was already paid in the Sonnet run.

**Issues seen with Haiku (low and medium effort):**
- It uses "partial" less (16 to 17% of verdicts against 25% for Sonnet) and "not met" more (30% against 26%): it collapses a half-right idea into all or nothing.
- Its quotes are often not copied exactly: 18 to 23 of 120 answers carry an unverified quote, against 6 for Sonnet.
- It reads the model answer too literally ("never says X").
- It once mistook a requested list for a bare keyword list (guarded in code now).
- Given a schema with an optional field it did not need (deductions), it filled it in on 28 rubric files. The rubric writer now returns a schema without that field.
- Told about deductions, it applied them to 12 to 17 of 24 RiceChem answers when the teacher deducted in 2 (recall 1.0, precision 0.12 to 0.17). Deductions are therefore off by default (`deductions: false`) until a stronger marker is used. With them on, RiceChem error went 0.151 to 0.164; with a stricter prompt 0.174. RiceChem was used to develop this feature because no other set has deductions, so it is not a clean benchmark.

## 13. Generalising across subjects (maths, physics, language, AI)

Our datasets cover networks, AI, programming and chemistry. We have no maths or language data yet, so nothing below is tested on them.

Principle: keep the grading prompt generic ("does the answer carry the idea of this point") and put subject rules into the rubric, not into the prompt.
1. **Question profile.** Once per question, a strong model labels it (definition, explanation, calculation, derivation, list, comparison, code, essay) and writes the type's rules into the rubric. Examples: calculations give method marks and a final-answer mark with a stated tolerance and units; language answers weigh content and language quality separately; lists need N distinct items. The grader reads the rubric, so one prompt serves all subjects.
2. **Prompt modules chosen by question type, not by dataset.** Today policy files are chosen by dataset name. They should become a small set picked by the profile, so a new dataset needs no new prompt file.
3. **Numbers checked by code.** For calculations, code compares the final number with the reference within the tolerance. The model judges the working.
4. **Teacher-marked examples** of the same question type, retrieved at run time, when they exist. They are optional.
5. **How we will know it generalises:** tune on some types and test on a type held out entirely. This needs new data: a maths set and a language set (candidates to find).

## 14. Where other model families and a second model help

Only Claude models are available here, so these are design notes, not results.
- **A different vendor as the feedback judge.** A judge from the same family as the writer tends to prefer its own style. A different family removes that bias. Cost is small because the judge runs once per feedback.
- **A different family as the second opinion.** Same-model voting did nothing because the errors repeat. Errors from a different family are less correlated, so a disagreement is a better sign of a hard answer.
- **Specialised models for OCR.** Handwriting readers (TrOCR, GOT-OCR) are a different family of model, used only to turn images into text.
- **Code for numbers.** A small calculator or sympy check replaces a model for the arithmetic of final answers.

Two models without much extra cost:
1. **Strong model writes the rubric once, cheap model marks every answer.** Tested: Haiku with Sonnet rubrics took Mohler from 0.281 to 0.215 at Haiku's marking cost.
2. **Cascade.** Haiku marks everything; only answers it is unsure about go to Sonnet. Signals Haiku already gives: an unverified quote (15 to 19% of answers), a disagreement with a second cheap model, or a partial verdict on a heavily weighted point. If about a fifth of answers escalate, the cost is about Haiku plus 0.2 times Sonnet, about $0.85 per 120 answers against $3.00 for Sonnet alone. Not yet tested.
3. **Cheap model for reading and feedback, strong for marks.** Not yet tested; the read step is a third of the calls.

## 15. Status of the needs-improvement list

All four items were worked on with Haiku, using results already logged wherever possible. One new run per question, no repeats.

| Item | State |
|---|---|
| Deductions | Now usable **inside the cascade**: Haiku proposes, and every answer where it applied a deduction is re-marked by Sonnet (`escalate_when: [deduction]`). RiceChem, 24 answers, one run (`casc_rice`): mark error 0.174 to 0.135, QWK 0.70 to 0.85, deduction F1 0.29 to 0.40. Deduction precision is still only 0.25 (recall 1.0), so deductions stay off unless the cascade is on. |
| Marks shift with the model answer's wording | SAF, 40 answers, Haiku medium with Sonnet-written rubrics (two runs, compared with the logged `cmpM_saf`). Masking 30% of the model answer: error 0.151 to 0.154, mean mark change 0.04, 5% of answers move over 10% of the total: **stable**. Keeping only the first half: error 0.151 to 0.192, mean change 0.14: the reference lost real content, so lower marks are expected. Earlier Haiku-written rubrics moved more (0.100 to 0.179 on DigiKlausur). Sonnet-written rubrics are the fix. |
| Cost | The cascade is built (`escalate_model`, `escalate_when`: partial, mid, unverified, deduction) and its value was measured **free**, by pairing the logged Haiku and Sonnet runs on the same 120 answers (`autograde cascade --cheap A --strong B`). Mean error over DigiKlausur, SAF and Mohler: Haiku medium alone 0.176, Sonnet alone 0.146, Haiku with `mid` re-marked (16% of answers) 0.156, `partial+mid` (47%) 0.146, which equals Sonnet. At Sonnet about 14 times Haiku, `mid` costs about 3.2 Haiku units and `partial+mid` about 7.6, against 14 for Sonnet alone. Default triggers are partial, mid and deduction. The unverified-quote trigger helps little (0.176 to 0.166). The live cascade is verified once, on RiceChem. |
| Feedback length and the styles page | Measured on 36 formal feedbacks of answers that lost marks: median 180 words, 25% over the 220-word target, none over 280, so the old guard never fired. The guard now fires at 240 words. The styles page shows the current template. |

Still open: the Sonnet comparison of the full cascade, Mohler under-marking (Haiku reads the reference literally), maths and language data.

## 16. DeepSeek V4.1 Flash via OpenRouter, and partial credit fixed at 50%

DeepSeek V4.1 Flash (OpenRouter, Sonnet-written sized rubrics, marking only, 40 answers per set, seed 1) cost about $0.02 per set and took 3 minutes. Error against the teacher: DigiKlausur 0.127 (Haiku medium 0.162, Sonnet 0.131), SAF 0.141 (0.151, 0.128), Mohler 0.196 (0.215, 0.179). So it matches Sonnet on DigiKlausur at about 2% of Sonnet's cost and beats Haiku on all three. Those runs used partial = 0.9. From the saved verdicts (`calibrate`), partial = 0.5 gives SAF 0.119, DigiKlausur 0.159 and Mohler 0.221. The project rule is now partial = 50% unless the rubric or strictness level specifies otherwise, so the default is 0.5 and the numbers above are not comparable to future runs. Free OpenRouter models (Gemma, Nemotron) are refused until the account allows free endpoints that may train on prompts, and are limited to 50 requests a day.

## 17. New task types: first look (30 answers each, marking only)

Loaders are in `datasets/extra.py`; these sets are for measuring only and ignore the dev/test split. The pipeline is the full read, mark, check path with sized schemes written by the same model that marks. The baseline is one plain call per answer. Error is the mean absolute difference from the teacher as a share of the total marks. Partial credit is 0.5 (the project rule).

| Set (what it tests) | Marks | DeepSeek baseline | DeepSeek pipeline | Haiku baseline | Haiku pipeline |
|---|---|---|---|---|---|
| ASAP-SAS (science and reading answers, 0 to 3) | mean of 2 graders | 0.161 | 0.176 | 0.208 | 0.294 |
| SciEntsBank (school science, 5-way label to 1 / 0.5 / 0) | label | 0.383 | 0.383 | 0.350 | 0.300 |
| AES2 (persuasive essays, 1 to 6) | holistic | 0.078 | 0.211 | 0.122 | 0.160 |
| ProcessBench (maths step checking, pass or fail) | first wrong step | 0.000 | 0.000 | 0.000 | 0.010 |

Costs: Haiku pipeline about $0.05 to $0.10 per 30 answers, Haiku baseline $0.003 to $0.03, DeepSeek on Goedel $0. Haiku AES2 pipeline finished 27 of 30 (3 calls failed). Runs: `new_*` (DeepSeek) and `newH_*` (Haiku), configs `cmp_new.yaml` and `cmp_new_haiku.yaml`.

**What we learned**
1. **The pipeline does not beat the plain baseline on these types.** On the four sets it won once (SciEntsBank with Haiku). On the earlier short-answer sets it won because the schemes and a model answer were there. Here the structure is missing or does not fit, and 30 answers is a coarse sample (one answer is 3% of the answers), so treat the gaps as direction only.
2. **Essays need a holistic mode.** A list of points with marks over-credits an essay: the pipeline's bias was +0.18 with DeepSeek and +0.12 with Haiku, against +0.05 for the baseline. A 1 to 6 score is a judgement of content, organisation and language together, not a count of ideas. Plan: three scored criteria (content, organisation, language) with anchored levels, averaged by code.
3. **No reference answer hurts.** ASAP-SAS prompts for the reading sets carry no rubric text and the schemes are inferred from the question, so Haiku under-marks (bias -0.10). Plan: when a question has no reference, a strong model writes the scheme once from the question and the reading passage, and the teacher can correct it.
4. **SciEntsBank's labels are noisy.** Answers such as "The stimulus is her sight" against "seeing or hearing the cup fall", or "bend our bones" against "move bones", are labelled wrong while the model gives credit. The mapping of "partially correct" to 0.5 is arbitrary too. It is a weak guide for tuning and is best kept as a sanity check.
5. **Maths verification is easy for these models.** Both models solved the problems themselves and matched the first-wrong-step label on 29 or 30 of 30. The real tests will be harder: student errors that are wrong in subtle ways, partial credit across steps, and numeric answers with units. SciBench has the problems and answers but no student work, so synthetic wrong answers would be needed.
6. **Goedel allows 4 requests at once.** Eight parallel runs hit HTTP 429. Run one dataset at a time with at most 4 workers.
7. **Haiku runs need to be started 3 at a time.** Launching eight Claude CLI runs with six workers each stalled the session and left runs unfinished; they resume from saved rows.

**Where improvement is needed, by priority**
1. A holistic essay mode (finding 2).
2. A scheme-writing path for questions with no reference answer, using the passage (finding 3).
3. A numeric and unit check in code, and subject modules for maths and physics (finding 5).
4. Per-dataset calibration of the partial value and strictness from a few teacher-marked answers (`calibrate`).
5. Handwritten input through a vision model, then the same pipeline. EDU-CIRCUIT-HW has rubrics and TA labels but no problem text.
6. Mohler-style under-marking of paraphrases, through the cascade (section 15).

## 18. Current workflow, in one place

1. **Input:** question, model answer (or none), optional teacher rubric, the student's answer.
2. **Marking scheme (once per question, cached in `rubrics/`):** a strong model turns the question and model answer into weighted points. A teacher rubric is used as is. Variants: sized (default), atomic, lenient, moderate, harsh, official.
3. **Read:** the answer is summarised on its own: ideas, problems and form (explanation, short answer, keyword list, incoherent).
4. **Mark:** each point is met, partial or not met, with an exact quote. Code prices it: met is full, partial is 50% of the point's marks unless the rubric or level says otherwise.
5. **Checks in code:** the quote must be in the answer (otherwise flagged), the form gate (scrambled text 0, a bare keyword list at most half when an explanation was asked), deductions only if enabled.
6. **Cascade (optional):** a cheap model marks every answer; answers with a partial verdict, a mid-range total or an applied deduction are re-marked by a stronger model.
7. **Feedback:** formal register, built from the verdicts; no model call for full marks; a draft over 240 words is rewritten once.
8. **Logging:** every run is recorded in `experiments/` (score, settings, prompt fingerprint) and committed locally with a tag; `autograde history` lists them.

Backends: Claude CLI (Haiku, Sonnet), Anthropic API, OpenRouter, Goedel Machines (DeepSeek V4.1 Flash, free). The key rules are in section 16. Datasets: see DATASETS.md; tuning uses the dev splits of DigiKlausur, SAF and Mohler; EngSAF, RiceChem and the new sets are measurement only; the held-out test split is untouched.


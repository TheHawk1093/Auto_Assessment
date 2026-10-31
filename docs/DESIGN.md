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

## 19. Is feedback needed on the new sets, and does it help?

**Scope.** By the teacher's marks, the share of answers that lost marks (so need feedback): ASAP-SAS 27 of 30, SciEntsBank 24 of 30, AES2 27 of 27 (no essay got 6), ProcessBench 18 of 30. Only 10% to 20% of answers earn full marks on three of the four sets, so feedback is needed almost everywhere. Full-mark answers get the code-built shortcut with no model call.

**Which sets have a real reference.** SciEntsBank 30 of 30; ASAP-SAS 7 of 30 (only prompts 5 and 6 carry rubric text); AES2 and ProcessBench have only a generic guide I wrote. The pipeline's schemes are therefore well anchored only on SciEntsBank, which is also the set with noisy labels. This, not "no model answer" alone, is the likely reason the pipeline does not beat the baseline there.

**Gain from feedback (revision test, Haiku, runs `fbH_*`).** A simulated student rewrites the answer once with the feedback and once without (control); both are re-marked with the same scheme. Marks gained per answer:

| Set | Answers tested | Gain with feedback | Gain without | Lift | Improved / worse | Model answer copied into revision |
|---|---|---|---|---|---|---|
| SciEntsBank (1 mark) | 6 | +0.83 | +0.25 | +0.58 | 100% / 0% | 0.19 |
| ASAP-SAS (up to 3) | 7 | +0.79 | +0.29 | +0.50 | 100% / 0% | 0.00 |
| AES2 (1 to 6) | 1 | +0.50 | +0.13 | +0.38 | 100% / 0% | 0.00 |

Feedback helps in every case tested, by about 0.4 to 0.6 marks above a rewrite without it. The samples are tiny (the revision test keeps only answers that lost marks and could be rewritten, so AES2 gave one), the student and the grader are both Haiku, and the re-marking uses the same scheme that wrote the feedback, so it can overstate the gain. Treat it as evidence that the feedback is usable, not as a measured effect size.

**Not done.** There is no mark-and-feedback single-call baseline, so we cannot yet say how much of the lift comes from the pipeline's checked verdicts. The next step is that baseline on DigiKlausur, SAF, RiceChem and essays, scored with the revision test and a blind pairwise judge.

## 20. Exam input and the simplified workflow (the direction for the demo)

**What the teacher gives.** A question paper (all questions, marks per question or sub-question). Reference material for the questions: a model answer, a rubric, both in one file, or both in two files; for some questions possibly nothing. Student answers as typed text or as photographed sheets. In the interface: part-mark granularity (rubric / none / half / quarter), strictness and a free-text note. The teacher never labels the question type; the model infers `kind` (short, essay, maths) and `field` (subject area) from the paper.

**Reference cases, reduced to two (plus one for later).**
1. A rubric is present (with or without a model answer): the rubric is the scheme. A free-text rubric is only restructured into points, adding nothing; a rubric that is already JSON points adding up to the total is used as it is with no model call. The model answer goes to the marker as context.
2. Only a model answer: a strong model writes the points from it, with part-mark levels in the allowed steps; a self-test checks that the model answer scores full marks and "I do not know" scores almost none.
3. Neither (open-ended questions): the earlier path stays (the writer works out an answer key, a review pass audits the scheme). Not developed further yet.

**Steps** (`autograde exam`, code in `src/autograde/intake/`):
1. `paper.py`: the model splits the paper into questions with marks; a sub-question is a question of its own and carries the shared stem. A paper that is JSON is read without a model. Missing marks are refused, never guessed.
2. `reference.py`: the model copies the matching reference text to each question id (it writes or changes nothing); JSON keyed by id is read directly; questions without a reference are reported.
3. `answers.py`: a folder with one file per student (markers like `Q1.`, `Answer 2(a):`, `2 b)` are found by code; if too few are found the model splits the text), one JSON file, or the output folder of `autograde ocr` (sheet items are matched to the paper's ids loosely: `2(a)` = `2a`). Missing answers and stray answers are reported.
4. `exam.py`: one item per student per question. The exam's cache name carries a hash of the paper and references, so an edited question never reuses an old scheme.
5. The grading workflow below, unchanged, with feedback always on.
6. Outputs in `runs/<name>/`: `schemes.md` (the teacher reads this first; `--schemes-only` stops here), `marks.csv`, `students/<student>.md` (marks, feedback, flags for the teacher), `intake.json` (what was parsed and the warnings).

**Grading workflow (per answer, unchanged).** Read-first summary of what the student wrote; mark each point met / partial / not met with an exact quote; code prices the verdicts (met = full, not met = 0, partial = the point's own level, else the teacher's granularity, else 50%); code checks (quote present, form gate, deductions only if the teacher gave them); optional cascade; feedback.

**Feedback is mandatory** for every answer that lost marks (a perfect answer gets a message built in code). `with_feedback: false` exists only as a measurement shortcut.

**Prompt routing hooks.** Prompts per answer type and per subject field are not written yet. Adding `grade.kind.<kind>.system.md`, `grade.field.<field>.system.md` or `rubric.field.<field>.system.md` is picked up automatically (`prompts.optional`); nothing else changes.

**Demo run** (`examples/exam_demo/`, DeepSeek on Goedel for everything, 3 students, 4 questions, 12 marks): the paper split into 4 questions with the right marks and inferred type and field; the combined reference file was matched per question (Q3 had a model answer only, 2a and 2b were mixed); half-mark granularity produced one 0.5 level per point; a blank answer was reported and marked 0. Marks: model-answer-only reference alice 11, bob 2, cara 9; combined 12, 3, 8.5; rubric-only for Q1/2b with 2a and 3 derived 12, 2, 9. Model-answer-only gave alice 3/4 on Q1 where the combined reference gave 4/4 (the rubric had said half marks for naming an idea; the derived scheme is stricter): the same answer can move one mark with the reference given, which is expected but worth showing the teacher through `schemes.md`.

**Defects found by the demo and fixed.** (a) DeepSeek returned empty quotes for correct credited points, which the "flag" policy only reported (noise on every answer); credited points with no quote at all now trigger the one retry. (b) The full-marks feedback cut the idea at "e.g."; fixed. (c) A missing `--config` file silently fell back to the defaults (see section 21); it is now an error.

## 21. Solid scheme writer: experiments, an invalid batch, and what is open

**What changed in the writer** (variant `solid`): a strong model writes the scheme (Sonnet in these runs), with part-mark levels (a share and a description each) so partial credit comes from the rubric, band-style criteria for essays, steps plus a worked solution for maths, an answer key when there is no reference, and a review pass when there is no reference. Teacher inputs change the cache folder through a hash. Unit tests only; the teacher inputs have not yet been used in a measured run.

**An invalid batch, recorded for honesty.** Nine of ten first pipeline runs were launched with the config path missing its `.yaml` extension; the loader silently used the defaults, so they ran Sonnet with old rubrics and feedback. They are kept, unused, in `runs/_invalid_default_config/`, were rerun with the right config, and a missing config file is now an error. Two hard-set chains also failed once on a Claude CLI error (probably the usage limit) and were rerun. One DeepSeek hard-maths answer hung for over ten minutes and was stopped, so that run has 29 answers.

**Results** (30 answers per set, seed 1, error as a share of total marks, bias in brackets; "old" is the earlier pipeline where the marking model wrote its own scheme; "solid" is Sonnet-written schemes; Haiku was not run on the two hard sets):

| Set | DeepSeek baseline | DeepSeek old | DeepSeek solid | Haiku baseline | Haiku old | Haiku solid |
|---|---|---|---|---|---|---|
| ASAP-SAS | 0.161 | 0.176 | 0.258 (-0.07) | 0.208 | 0.294 | 0.275 |
| ASAP-SAS without set 4 | 0.163 | 0.172 | 0.216 | 0.193 | 0.265 | 0.239 |
| SciEntsBank | 0.383 | 0.383 | 0.367 | 0.350 | 0.300 | 0.317 |
| AES2 essays | 0.078 | 0.211 (+0.18) | 0.132 (+0.11) | 0.122 | 0.160 | 0.119 (+0.01) |
| IMO-GradingBench (0 to 7) | 0.476 (+0.45) | - | 0.406 (+0.33) | 0.336 (+0.17) | - | - |
| ProcessBench hard (29) | 0.067 | - | 0.161 (-0.05) | 0.067 | - | - |

**Findings.**
- Essays: band rubrics cut the over-marking a lot (DeepSeek 0.211 to 0.132, Haiku 0.160 to 0.119, now level with its baseline). DeepSeek's one-call baseline (0.078) is still better.
- ASAP-SAS: no gain for DeepSeek (worse, 0.176 to 0.258, now under-marks), a small gain for Haiku. Set 4 is a data defect: its prompt holds two different questions and students answered either, so no scheme fits. Where the set carries a real teacher rubric (sets 5 and 6, 7 answers) the pipeline beat the baseline (0.07 and 0.08 against 0.10 and 0.17 on 5 and 2 answers: indicative only).
- SciEntsBank: about the same as before; its labels are noisy.
- IMO proofs: every model over-marks heavily (zero-scored proofs get 5 of 7 on average from DeepSeek). The pipeline beats the DeepSeek baseline (0.406 against 0.476, correlation 0.42 against 0.12) but Haiku's one call (0.336) is better than both. Proof grading needs a stricter, step-by-step check than our point scheme gives.
- ProcessBench hard: accuracy 86% for the pipeline against 93% for both baselines; with 30 answers and 9 correct solutions this is within noise, but there is no sign of a gain.
- Cost: the Haiku runs cost $0.06 to $0.13 each plus Sonnet scheme writing; the DeepSeek runs are free. The OpenRouter main key is unused ($20 limit, $0.00002 spent).

**Not done.**
- The older datasets (DigiKlausur, SAF, Mohler, RiceChem, EngSAF) were not rerun with the solid writer, so it is not yet the default; run that regression first.
- The new rubrics have not been tested together with feedback (revision test).
- Case 1 (rubric given) was demonstrated only through the demo exam and unit tests, not measured.
- OCR is not tested end to end through `autograde exam`; the answers loader accepts the OCR sheet files, but photos to marks has not been run. The VLM OpenRouter key is not in `.env` (only Gemini, OpenRouter main and Goedel are).
- Objective questions (multiple choice, single numbers), multi-part marking beyond independent sub-questions, units and numeric checks, code, and figures are not built.
- Per-type and per-field prompts are not written (hooks exist).

**Next steps, in order.** (1) Regression of the older datasets with the solid writer and decide the default. (2) Revision test of feedback on the solid schemes and a single-call mark-and-feedback baseline. (3) Strict step-wise mode for proofs (IMO) and calibration of the over-marking. (4) OCR end to end on the Mendeley exam set through `autograde exam`. (5) The objective question type in code. (6) Per-type and per-field prompts, then benchmarking other models (Qwen via OpenRouter at about a cent per run) and the Sonnet comparison once, then the held-out test.

## 22. Harshness, feedback wording and Indic languages: what was tested, and what was not changed

**Where the marker's negative bias comes from.** On Mohler (30 answers, DeepSeek, about -0.20 of the total), answers that the teachers gave full marks still scored 0.98 of the total, so the marker is not harsh on good answers. The loss is on partly right answers, which the teachers (their average) rewarded generously: a binary tree with the ordering reversed got 4 of 5. The schemes also split a one-sentence model answer into extra points (for example a point for "control passes to the first statement of main" when the model answer says only "at the main function").

**Three attempts, tuned on Mohler seed 1 and checked on Mohler seed 7 plus DigiKlausur and RiceChem (seed 7).** Error as a share of the total, bias in brackets, 30 answers each:

| Set | solid (control) | solid.core | solid.core + strictness lenient |
|---|---|---|---|
| Mohler seed 1 (tuned) | 0.225 (-0.205) | 0.220 (-0.200) | 0.193 (-0.180) |
| Mohler seed 7 | 0.203 (-0.197) | 0.192 (-0.185) | 0.166 (-0.134) |
| DigiKlausur seed 7 | 0.248 (-0.073) | 0.269 (-0.119) | 0.280 (-0.063) |
| RiceChem seed 7 | 0.121 (+0.046) | 0.100 (+0.008) | 0.091 (+0.067) |

- `solid.core` (`prompts/rubric/rubric.style.core.system.md`: points only from facts the reference states, never more points than facts, the central fact at least half the marks) moves the error by -0.005, -0.011, +0.021 and -0.021. That is inside the noise of 30 answers, so it is **not** made the default. It stays as an opt-in writer style (`rubric_variant: solid.core`).
- `strictness: lenient` helps the one lenient teacher (Mohler, both samples) and does not help the others. It is a teacher setting, not a default.
- The partial-credit weight does not matter here (0.3 to 1.0 moves the error by 0.005): only 9 of 55 verdicts are partial.
- `autograde calibrate` fitted on seed 1 and applied to seed 7: the mark stretch picks 1.5 on Mohler (error 0.192 to 0.152, same level 0.53 to 0.67) and 1.0, no change, on DigiKlausur and RiceChem. So it adapts to the teacher and leaves a teacher who needs nothing alone. It is not wired into the pipeline: a stretch changes the total without changing the per-point verdicts, so the marks and the feedback would disagree.

Net: no global prompt change was adopted for the bias. It is a property of the teacher, and the evidence says to set it per teacher from a marked sample.

**Feedback wording (`concrete` against `formal`).** The judge notes on English feedback said the `fix` was often study advice ("revisit ...") and the `why` sometimes only restated the gap. `prompts/feedback/feedback.concrete.system.md` asks for a specific change to this answer and a real reason. It was written looking only at English (`tr2_english`) and then run unchanged on Hindi, Marathi, Tamil, Bengali and the real Marathi set (ScAA), with marks and schemes unchanged (`refeedback`). Haiku judge pass rates and revision results, formal to concrete:

| Set | actionable | explains why | correct | revision gain | leakage |
|---|---|---|---|---|---|
| English | 0.68 to 1.00 | 1.00 to 1.00 | 0.93 to 0.90 | 0.55 to 0.55 | 0.05 to 0.08 |
| Hindi | 0.83 to 1.00 | 0.70 to 0.95 | 0.90 to 0.93 | 0.62 to 0.63 | 0.06 to 0.07 |
| Marathi | 0.91 to 1.00 | 0.96 to 0.96 | 0.97 to 0.93 | 0.58 to 0.58 | 0.15 to 0.16 |
| Tamil | 0.71 to 1.00 | 1.00 to 0.91 | 0.97 to 0.93 | 0.58 to 0.58 | 0.11 to 0.11 |
| Bengali | 0.67 to 1.00 | 0.89 to 0.78 | 1.00 to 0.87 | 0.69 to 0.69 | 0.03 to 0.06 |
| Marathi ScAA | 0.94 to 1.00 | 0.70 to 0.94 | 0.92 to 0.92 | 0.97 to 0.97 | 0.35 to 0.42 |

Reading: the judge finds the fixes more actionable everywhere (that is the criterion the prompt targets, so part of this is the judge following the wording). "Explains why" improves in Hindi and ScAA and falls in Tamil and Bengali, "correct" falls by 0.03 on average, and leakage rises a little. The revision test cannot tell the two apart: the simulated student reaches nearly full marks with either, so the gain equals the marks lost (a ceiling). Because the judge is not validated on Indic text, `concrete` is **not** the default. `judge-sheet` wrote 60 feedbacks (30 answers, both variants, shuffled) for a person who reads the languages; `judge-agreement` then gives agreement and kappa per question (`artifacts/judge_check/`). Decide the default after that.

**Language handling is separate from English.** Everything specific to a language is under `prompts/language/` (`language.feedback` with a `{language}` slot, one register note per language, the translation prompts) and in `localize.py` (fixed labels for Hindi, Marathi, Tamil and Bengali; the Tamil and Bengali wording is not checked by a native speaker). English prompts never contain language text: `feedback._system` adds the language note only when `feedback_language` is set (tested). Marking, schemes and every other prompt are language-neutral.

**Translated Mohler, 30 identical answers per language** (English is the control; DeepSeek marks, Haiku judges and plays the student):

| | English | Hindi | Marathi | Tamil | Bengali |
|---|---|---|---|---|---|
| Error / bias | 0.26 / -0.24 | 0.23 / -0.21 | 0.28 / -0.26 | 0.26 / -0.24 | 0.28 / -0.25 |
| QWK | 0.50 | 0.49 | 0.46 | 0.50 | 0.48 |
| Revision gain with / without feedback | 0.55 / 0.16 | 0.62 / 0.18 | 0.58 / 0.10 | 0.58 / 0.06 | 0.69 / 0.14 |
| Lift | 0.39 | 0.44 | 0.48 | 0.52 | 0.55 |

Marking quality does not depend on the language, and feedback helps in each (no rewrite got worse). Real Marathi (ScAA, 24 answers): DeepSeek 95.8% same level, QWK 0.975; revision 0.97 with feedback against 0.09 without, with 35% leakage (word overlap with the feedback), so that gain is an upper bound.

**Code sandbox.** The wasm interpreter has not been run by the agent (the permission classifier blocked it three times). `tests/test_sandbox_real.py` (opt-in, `AUTOGRADE_REAL_SANDBOX=1`) checks it for pass/fail counting, syntax errors, no network, no writes outside, an endless loop, a memory hog and a forged result. `tools/sandbox/README.md` records where the binary came from and its checksum.

**EDU-CIRCUIT-HW.** Run on Gemini; result and the reason it is the wrong framing in section 23.

## 23. EDU-CIRCUIT-HW result, a literature survey, and ideas ranked by what our own data says

**EDU-CIRCUIT-HW (30 transcribed dev pages, Gemini Flash Lite writes the scheme and marks).** Error 0.303, bias -0.30, QWK 0.00, correlation 0.12, 70% of answers flagged for an unverified quote. The framing explains it: the TAs start from full marks and take off 0 to 11 (mean human mark 0.98, spread 0.02), so a constant 98 has error 0.016. The pipeline's point scheme starts from zero and the transcripts are short (median 268 characters), so almost nothing can be credited or quoted. This is a wrong design for the data, not a measure of the marker. The task is **detecting the TA's listed errors**, so it needs a scheme with one full-credit point plus the TA's deductions, marked as "start at full, subtract only an error that is visible in the transcript", and it should be scored on whether the deducted criteria match the TA's (precision and recall), not on the total. Marking with Goedel/DeepSeek still hangs on the long scheme prompts. Not yet built.

**Literature read (abstracts and search summaries, not full papers).**
- Rubric-conditioned grading, SciEntsBank, Qwen 2.5-72B ([arXiv 2601.08843](https://arxiv.org/abs/2601.08843)): agreement with experts is strong for binary rubrics and drops as the rubric gets finer; a consensus-based deferral ("trust curve") raises accuracy on what is kept; the model resists prompt injection and is sensitive to synonym swaps.
- CHiL(L)Grader ([arXiv 2603.11957](https://arxiv.org/abs/2603.11957)): temperature-scaled confidence, selective prediction; it auto-scores 35 to 65% of answers at QWK 0.80 or more and sends the rest to a person.
- LLM graders against TAs on UML diagrams ([arXiv 2603.16357](https://arxiv.org/abs/2603.16357)): per-criterion accuracy up to 88.6%, close to a TA. A claim in a search summary that most models were harsher than the TAs was not in the abstract and is unverified.
- Feedback quality: judges lean positive and prefer their own outputs; actionability and completeness stay the weak points of LLM feedback; revision outcomes are used beside ratings (FeedEval, [arXiv 2511.07628](https://arxiv.org/abs/2511.07628), and reviews found by search).
- Handwriting: vision models "fix" a student's errors when transcribing, which hides what the marker needs (a 2026 EMNLP paper proposing the PINK metric; [ACL 2025 long.720](https://aclanthology.org/2025.acl-long.720) on handwritten maths). Reference answers and rubrics improve alignment.
- Indic: ScAA ([ICON 2020](https://preview.aclanthology.org/setup/2020.icon-main.58)) is the only short-answer grading set found for Hindi and Marathi; nothing for Tamil or Bengali. MILU and IndicQuest test knowledge, not grading. Our translated sets are therefore a stopgap, not a benchmark.

**Ideas, in the order I would do them.**
1. **Send doubtful answers to a person (selective marking).** Free test on runs we already have: the spread of the marks from three scheme variants on the same 30 answers, as the doubt signal. Keeping the 60% with least disagreement lowers the error from 0.181 to 0.132 on Mohler and from 0.103 to 0.076 on RiceChem; on DigiKlausur it barely moves (0.263 to 0.256). In-sample, 30 answers, no threshold fitted, so it is only a sign. Build it as a flag the `exam` command already half has (`votes`, `second_model`, `escalate_*`) plus a report of the share kept and the error on it.
2. **Per-teacher calibration from a marked sample.** Section 22 showed the fit transfers on Mohler. Next: fit on about 20 marked answers a per-point "credit for a missing supporting detail" instead of a total stretch, so verdicts and totals stay consistent.
3. **Deduction-first scheme for "start at full" marking** (circuit and similar): see above. Score the detected errors.
4. **A revision test that does not saturate.** The simulated student reaches near-full marks with any feedback, so it cannot rank feedback styles. Options: a weaker student model, one improvement addressed per rewrite, or an uptake check (did the rewrite fix each flagged issue). Add a second judge from another family and report kappa against the person-filled sheet before adopting `concrete`.
5. **Faithful transcription.** For handwriting and the circuit pages, instruct "copy, do not correct" and measure how often the transcript hides an error (PINK-style: penalise a transcript that earns more marks than the page).
6. **Robustness tests we can already build:** synonym swap (the 2601.08843 weakness) and a round trip through another language (translated sets exist), and non-native phrasing, checking that marks do not move.
7. **Keep rubrics coarse.** Agreement falls with granularity; our over-split schemes agree with that. A cap on points per question tied to the number of facts in the reference is the generic form of `solid.core`, which was neutral on its own.

## 24. Learnings, decisions and changes so far (written 2026-10-29, before the next round)

**Decisions taken by the project owner.**
- The pipeline must mark and write feedback on its own. A person is never required.
- No calibration of the marker. The pipeline follows the model answer and the rubric strictly; a teacher's leniency is an input (`strictness`, rubric, notes), not something fitted.
- Flags exist only where a person's look is useful (real ambiguity, disagreement, doubtful evidence), shown in the report as optional "worth a look". Flag rate and necessity are measured.
- Faithful transcription of handwriting is to be fixed. EDU-CIRCUIT-HW is parked.
- Feedback is analysed for content and for the system prompt, not only style, with weak student models.
- Robustness is tested against many perturbations, not synonym swaps alone.

**What was built** (details in sections 20 to 23 and in CLAUDE.md).
- Intake: figures in answers and references; kinds mcq, numeric, code, diagram, maths with their own code checks; multi-part follow-through; teacher controls (strictness, partial credit, mark step, notes).
- Code questions: sandbox in WebAssembly (default), docker or process; generated tests that a reference solution must pass; code using numpy is flagged `code_needs:` and judged by reading. The WebAssembly interpreter has never been run by the agent (blocked three times); `tests/test_sandbox_real.py` is the opt-in check.
- Languages: Marathi (real data), Hindi, Marathi, Tamil, Bengali (translated Mohler). Feedback comes out in the student's language; labels in `localize.py`; all language-specific prompts in `prompts/language/`.
- Evaluation: revision test, judge, `judge-sheet` and `judge-agreement` for a person to check the judge, translated datasets, experiment log.
- Layout: prompts in stage folders found by name, one-off configs in `configs/experiments/`, shell chains in `scripts/`, OCR tools in `tools/ocr/`, `wasmtime` declared as the `sandbox` extra, the experiment log fingerprints every prompt and skips runs that marked nothing.

**What the measurements say.**
- Marking is language-neutral on translated Mohler (error 0.23 to 0.28, QWK 0.46 to 0.50 in all five languages). Real Marathi: 95.8% same level, QWK 0.975 (24 answers).
- The negative bias on Mohler comes from partly right answers the teachers rewarded generously, not from good answers (those score 0.98). Scheme style `solid.core` was neutral (inside noise); `strictness: lenient` helps only a lenient teacher. No default changed.
- Feedback helps in every language (revision gain 0.55 to 0.69 with feedback against 0.06 to 0.18 without), but the revision test saturates with a Haiku student, so it cannot rank feedback styles. `concrete` feedback raised the judge's "actionable" rate to 1.00 everywhere, lowered "correct" by about 0.03, and is not the default until a person has checked the judge.
- Disagreement between scheme variants separates better-marked from worse-marked answers on Mohler and RiceChem (error 0.181 to 0.132 and 0.103 to 0.076 on the 60% kept) and hardly at all on DigiKlausur. 30 answers, in-sample.
- EDU-CIRCUIT-HW: the point scheme from zero is the wrong framing (human mean 0.98, constant 98 has error 0.016, ours 0.30). Parked.

**Process lessons.**
- Tune on one sample, confirm on another sample and on other datasets, and adopt only what survives; most "improvements" at 30 answers are noise.
- A judge that is also told what to optimise (the prompt names the judge's criterion) overstates the gain; check against a person.
- Heredocs with quotes and backslashes break in this shell; write files with the Write tool.
- Goedel hangs on very long prompts; Gemini's free daily quota runs out; DeepSeek jobs run one at a time.

## 25. Faithful transcription, evidence checks, review flags, feedback content and robustness (2026-10-29)

**Faithful transcription (`ocr/faithful.py`, run with `python -m autograde.ocr.faithful`).** Question: does a reader copy a student's mistake or quietly repair it? 43 handwriting-style pages (typed in script fonts, so reading is easy and any repair is the reader's own doing) hold planted mistakes: wrong facts, wrong numbers and units, misspellings, and 12 multi-line working with a slip that contradicts the line above, in English, Hindi, Marathi, Tamil and Bengali. Result: **readers almost never repaired a mistake.** With the current prompt, Gemini Flash Lite and Haiku kept 95.3% of the mistakes, repaired none, and lost 4.7% to glyph misreads ("H3O" read as "H30"); With a bare "transcribe the handwriting" prompt Sonnet kept 12 of 12 multi-line slips, Gemini repaired none and Haiku repaired 1 of 43. Even a deliberate "transcribe into clean, correct text" prompt produced 0 repairs on Gemini and Haiku. So this test cannot tell prompts apart and does not reproduce the earlier slip (a Sonnet repair of a wrong matrix entry on a real photographed page, before the "copy exactly" rule existed). What remains is risk on ambiguous real handwriting, where a reader may use context to settle an unclear glyph. Safeguards that exist or were added: the transcription prompts say to copy mistakes and mark doubtful characters `[?x?]`; a result whose answer contains `[?` is now listed for review (`ocr_unsure`); the reader never sees the model answer. Not built: a second reader whose disagreement is flagged (needs real handwriting with known mistakes to test).

**Evidence checks made more robust (`pipeline/verify.py`).** Over 3,904 stored markings, credit whose quote was not found in the answer fell into two kinds: 48% near copies (a typo corrected, a symbol dropped) and 47% no quote at all; 3% reworded, 2% a quote from the model answer.
- Near copies: error 0.119 against 0.161 for fully verified answers, so they are harmless. A quote of 24 or more characters now counts as found when at least 85% of it matches in runs of 4 or more characters, close together (`_near_copy`).
- No quote: error 0.255, but removing that credit makes it 0.630 (Mohler 0.21 to 0.86): the credit is mostly right and the marker forgot to quote. On an answer of 25 words or fewer the answer itself is now the evidence (`repair`); on a longer one the credit is kept and listed for review. Locating a supporting sentence by word overlap did not predict doubtful credit (error 0.262 against 0.232) and was dropped.
- Effect: answers with unverified credit fall from 5.8% to 3.2%.

**Review flags (`pipeline/review.py`, `autograde review --name R`, "Worth a look" in `report.html`).** Optional and never required. A result is listed when: the marker was asked again or repaired (`marking_unstable`), the scheme failed its self-test, credit has no verifiable quote, a second marker disagreed or a stronger one re-marked, a form rule or deduction applied, the handwriting reader was unsure, a drawing could not be checked, or a partly right answer lands mid-range (0.3 to 0.7 of the total with partial credit worth at least 20% of the total). Empty and nonsense answers are never listed (marked right every time). Measured over 3,872 answers in finished runs with teacher marks:

| | listed | error listed / rest | badly marked (error >= 0.25) listed / rest | share of all badly marked caught |
|---|---|---|---|---|
| all | 19.8% | 0.236 / 0.150 | 43.9% / 27.3% | 28.5% |
| DigiKlausur | 18.6% | 0.224 / 0.111 | 41.3% / 20.4% | 31.6% |
| Mohler | 20.0% | 0.286 / 0.214 | 54.5% / 38.7% | 26.1% |
| SAF | 7.2% | 0.141 / 0.106 | 35.7% / 22.1% | 11.2% |
| RiceChem | 42.9% | 0.181 / 0.128 | 32.1% / 18.1% | 57.1% |
| ASAP-SAS | 8.3% | 0.229 / 0.252 | 41.7% / 51.5% | 6.8% |

Reading: a person who reviews the listed fifth of answers sees answers that are marked about 1.6 times as badly, and half of the listed ones are fine (so the flag is a hint, not a verdict). It does not work on ASAP-SAS (inverted, small n), lists too many on RiceChem (partial credit is normal there), and the biggest single reason is the mid-range partial (351 of 3,872). The partial-credit threshold was chosen from four variants on the same data it is scored on, so the numbers are in-sample.

**Feedback content and system prompt.** What the feedback says, measured on English (`tr2_english`) and then on Hindi, Marathi, Tamil, Bengali and real Marathi:
- It is long: median 210 words for answers that lost marks, with one or two missed points; only 44% of the issues quote the student's words.
- Most judge complaints about correctness are the feedback calling a true student statement wrong, because the marker's verdict said so (the static array case): feedback inherits the marker's errors.
- `concrete` v2 (`prompts/feedback/feedback.concrete.system.md`): concrete fix, a real reason, length matched to the marks lost, and "incorrect" only when the question or model answer contradicts the statement. Judge pass rates, formal to concrete v2: actionable 0.68, 0.83, 0.91, 0.71, 0.67, 0.94 to 1.00 in all six sets; correct 0.93 to 0.93 (English), 0.90 to 0.93 (Hindi), 0.97 to 1.00 (Marathi), 0.97 to 1.00 (Tamil), 1.00 to 0.90 (Bengali), 0.92 to 0.88 (real Marathi); explains why 1.00 to 1.00, 0.70 to 0.83, 0.96 to 1.00, 1.00 to 0.90, 0.89 to 0.81, 0.70 to 0.84. The length rule barely worked (median 210 to 194 words English, 191 to 192 Hindi, 131 to 151 Marathi).
- Revision test with the weakest student (Gemini Flash Lite), formal against concrete v2: gain 0.55 against 0.55 (English), 0.62 against 0.63 (Hindi), 0.58 against 0.58 (Marathi); per-point uptake 100% and harm 0% for both. **The test saturates even with the weakest student**, because the student prompt lets it use only the answer and the feedback, so any feedback that names the missing idea is copied into the answer. It measures what the feedback hands over, not how well it guides. Tamil, Bengali and real-Marathi weak-student runs hit Gemini's daily quota and are not done.
- Added: per-point `uptake` and `harm` in the revision summary, and `--own-knowledge` (the student may also use what it knows, prompt `eval/revise.own`), which is the protocol that could separate feedback that guides from feedback that gives the answer. Not yet run.
- Decision: `formal` stays the default; `concrete` v2 is opt-in. It makes the judge's "actionable" 1.00 but "correct" and "explains why" move both ways by language, and the judge is not yet checked by a person (the 60-row sheet is waiting). Concrete v1 (section 22) differed only in the length and "incorrect" rules.

**Robustness (`autograde robustness --name R`, `evaluation/robustness.py`).** Each finished answer is rewritten without changing what it says, marked again with the same scheme, and the shift in marks (share of the total) is compared with a control: re-marking the unchanged answer. 15 variants: spelling slips, lower case and no punctuation, UPPER CASE, shuffled sentences, text-speak, filler, an irrelevant sentence, the question repeated (code, no model call); paraphrase, synonyms, non-native phrasing, informal, wordy (DeepSeek rewrites, cached); and half the answer (must lower the mark). Mean absolute shift (share of the total; share of answers that moved by 0.1 or more in brackets), 30 answers each:

| Variant | Mohler | DigiKlausur |
|---|---|---|
| control (same answer re-marked) | 0.022 (10%) | 0.046 (17%) |
| spelling | 0.025 (13%) | 0.031 (17%) |
| case and punctuation | 0.022 (10%) | 0.040 (17%) |
| UPPER CASE | 0.032 (17%) | 0.044 (20%) |
| shuffled sentences | 0.000 (n=4) | 0.026 (9%, n=22) |
| text-speak | 0.025 (13%) | 0.035 (20%) |
| filler | 0.029 (17%) | 0.029 (17%) |
| irrelevant sentence | 0.013 (10%) | 0.046 (23%) |
| question repeated | 0.017 (10%) | 0.037 (17%) |
| paraphrase | 0.055 (13%), mean shift -0.038 | 0.054 (20%), -0.013 |
| synonyms | 0.069 (20%), -0.032 | 0.029 (13%), -0.017 |
| non-native | 0.022 (10%) | 0.037 (10%) |
| informal | 0.029 (13%) | 0.058 (23%) |
| wordy | 0.015 (7%) | 0.046 (20%) |
| half the answer (should drop) | 0.284, 53% went down (n=19) | 0.392, 96% went down (n=26) |

Reading: the marker's own re-marking noise (0.02 to 0.05) is as large as most effects, so spelling slips, shouting, filler, text-speak, an irrelevant sentence, the repeated question and non-native phrasing do not move marks beyond noise. Paraphrase and synonym swaps pull Mohler marks down (-0.03 to -0.04, above noise at n=30 but not on DigiKlausur): the marker leans on the model answer's wording a little. Cutting the answer in half lowers the mark in 53% (Mohler) and 96% (DigiKlausur) of answers, so the test can see a real change. RiceChem and Hindi runs stopped on DeepSeek's daily token limit and are pending. The noise is the larger finding for review flags: a single marking is not repeatable within about 0.03 of the total.

**Still open.** DeepSeek and Gemini daily limits ended the runs at 20:51 IST; DeepSeek resets at 05:30 IST. Pending: robustness on RiceChem and Hindi, weak-student feedback runs for Tamil, Bengali and real Marathi, the `--own-knowledge` protocol, the person's check of the judge sheet, a real handwriting set with known mistakes for the transcription check, the sandbox run.

## 26. Marking that stays inside the teacher's rubric (2026-10-30)

**Why.** On a real paper (ME5309 mid-sem, TA rubric with global rules in Part A) the pipeline broke two of the rubric's own rules, found by checking its marks against the rubric text, not against the dataset's reference marks (those were written under a different scheme and are not used as truth): (1) a correct final answer with no formula scores zero, but the scheme writer had added a half-credit level for it and numeric points checked by code gave full credit to a bare number (b2_S56 got 2.5 of 4 on Q1a for bare values); (2) whole marks only, halves where a note names one, but a point without levels fell back to a 50% partial share (2.5 of 3 on Q1b for an arithmetic slip, where the rubric says 2). Q4b was a different matter: the pipeline took 1 of 2 from 21 of 30 students for missing the "Nff outside the feedback path" explanation because the rubric asks for it, so it was right.

**What changed.** Exam-wide rules are read from the documents, once per exam (`intake/rules.py`): `ExamRules` holds `working_required`, `part_marks` (unstated, stated_only, none, half, quarter), `mark_step`, `follow_through` and `notes` (other exam-wide sentences, close to the rubric's words). `apply_rules` builds the `TeacherInputs`; explicit flags win and `--ignore-rubric-rules` disables the step. The rules are printed at the top of `schemes.md`, so the teacher sees what was read. New part-mark mode `stated`: a point has part marks only where the rubric lists levels, any other point is all or nothing (prompt `grade.stated`, scheme-writer line in `teacher_block`). The solid scheme writer is told to add no level, leniency or deduction the rubric does not state. `working_required` is enforced by code: the first-pass reader records `working_shown` and `apply_working_gate` zeroes every point of a part whose scheme has a numeric answer when only bare values were written (flag `no_working`, reason shown in the feedback). Conceptual parts are untouched.

**Check.** On this rubric the extractor returned working required, part marks stated only, carry-through within a question, the arithmetic-slip rule, units and significant figures, with no flags passed. Marks of the rerun against the rubric rules: see the ME5309 results folder.

**Best of n and struck-out questions (`intake/counting.py`).** Papers that say "answer any three of four" count each student's best n top-level questions (2a and 2b belong to question 2). `ExamRules.count_best` is read from the paper; `--count-best N` overrides it. A question the student struck out is not marked at all (as the rubric says): the teacher gives it with `--struck-out STUDENT=Q` (repeat, or 1,3), since a pen strike-through is not visible in extracted text. Counting only adds up marks after marking, so schemes and cached results are untouched. `marks.csv` gets `counted_total`, `counted_out_of` and `counted_questions`; each student file shows the counted questions, marks the others "(not counted)" and says which question was struck out. Automatic detection of struck-out work (from the sheet or the image) is not built.

**Result on ME5309 (30 students, Haiku marking, Sonnet schemes) and what the audit found.** Checked against the rubric's own rules, not the zip's reference marks. Of 14 parts zeroed by the working rule, 13 were bare final values (the rubric says zero) and 1 was a false positive (a balance stated in words); before the reader prompt was tightened it was 4 of 17. Non-whole part marks fell from 14 to 7, all halves the rubric names (Q2a, Q3a). A sign-flipped G on Q1c, which the numeric check had credited because a spaced minus (`x - 0.09u`) was read as positive, is now caught. The scheme writer's default 20% unit penalty (not in the rubric) was removed when a rubric is given. The mean counted total fell from 18.6 to 15.1 out of 30 against the run without these rules, from the zeroed bare answers, whole-mark rounding and the removed unit penalty. 27 of 489 verdicts were zeroed because the marker said partial on a point with no level. Open: how often the working reader is wrong beyond this sample, the partial-on-no-level cases (should be shown to the teacher), and automatic detection of struck-out work.

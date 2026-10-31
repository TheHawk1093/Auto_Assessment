# Data credits and usage guide

This document acknowledges the authors of every dataset that autograde loads or was evaluated on,
states the licence under which each is made available, and explains how each may be used in this
project. All rights in the datasets remain with their original authors. Nothing in this repository
relicenses them.

## 1. Principles of use

1. **Attribute.** Cite the original paper or dataset (Section 4) in any report, paper or release
   that uses results obtained with these data.
2. **Respect the licence.** Check the licence column before redistributing, modifying or using a
   dataset commercially. Non-commercial (NC) and share-alike (SA) terms are called out below.
3. **Tune on development data only.** Datasets marked *development* may be used to tune prompts,
   switches and schemes. Datasets marked *benchmark only* are used to report results and are never
   tuned on (`BENCHMARK_ONLY` in `src/autograde/datasets/loaders.py`). Within a development dataset,
   questions are split into dev and test by a hash of the question id, so no question is in both.
4. **Do not store whole datasets in git.** Raw data is downloaded into `data/raw/` (git-ignored on
   every branch). Only small samples of datasets whose licence permits redistribution are committed
   (Section 3).
5. **Protect people.** Student writing is personal data. Use only anonymised, publicly released
   material, and never commit private course material (exam papers, answer sheets, marks).

## 2. Summary

| Dataset | Role | Licence | Sample in repo |
|---|---|---|---|
| DigiKlausur ASAG | Development (smoke test) | MPL-2.0 | Yes |
| SAF, Short Answer Feedback | Development (feedback quality) | Code MIT; data CC BY 4.0 (Hugging Face release) | Yes |
| Mohler et al. 2011 | Development (short-answer baseline) | CC BY 4.0 (Hugging Face mirror) | Yes |
| ProcessBench | Benchmark only (maths step errors) | Apache-2.0 | Yes |
| SciBench | Question pool (college science) | MIT | Yes |
| MathDial | Feedback and misconception tests | CC BY-SA 4.0 | Yes (share-alike applies) |
| IMO-GradingBench | Benchmark only (proof grading) | CC BY (Hugging Face release) | Yes |
| EngSAF | Benchmark only (engineering exams) | Apache-2.0 (Hugging Face copy) | No |
| SemEval-2013 Task 7 (SciEntsBank) | Benchmark only | Creative Commons (variant not verified) | No |
| ASAP-SAS | Benchmark only | Kaggle competition rules | No |
| ASAP/AES 2.0 essays | Benchmark only | CC BY-NC | No |
| IELTS essays with feedback | Feedback tests | Not verified | No |
| ScAA (Hindi, Marathi) | Development (Indian languages) | CC BY-NC-SA 4.0 | No |
| EDU-CIRCUIT-HW | Handwriting and circuit marking | Code Apache-2.0; data licence not stated | No |
| Mendeley digitised exam papers | Handwriting reading | CC BY 4.0 | No |
| IIIT Indic handwritten words | Indic handwriting reading | See source site | No |
| RiceChem | Benchmark only | None stated; available on request | **No** (never distributed) |

## 3. Obtaining the data

```bash
uv run autograde download              # DigiKlausur, SAF, Mohler  -> data/raw/
uv run autograde download --engsaf     # EngSAF (benchmark only)
uv run autograde download --samples    # ProcessBench, SciBench, SciEntsBank, MathDial,
                                       # AES 2.0, ASAP-SAS, IMO-GradingBench, IELTS (small cuts)
uv run autograde download --circuit    # EDU-CIRCUIT-HW rubrics, TA labels, a few page images
uv run python -m autograde.datasets.handwriting   # Mendeley exam and Indic word pages
```

ScAA is placed by hand under `data/raw/scaa/` from its public release. RiceChem must be requested
from its authors and placed by hand (see its entry). Then run, for example:

```bash
uv run autograde run --dataset digiklausur --split dev -n 24 --mode pipeline --name dk_dev
```

`dev` branch only: committed samples live in `datasets/samples/<name>/`, each with its licence text
and an attribution note, and are meant for offline tests and demonstrations, not for reporting
results.

## 4. Dataset entries

### 4.1 Development datasets

**DigiKlausur ASAG.** DigiKlausur project, <https://github.com/DigiKlausur/ASAG-Dataset>.
Neural-networks exam, 646 answers from 38 students on 17 questions, scores 0, 1 or 2, reference
answers. *Licence:* Mozilla Public License 2.0 (the licence file ships with the data; keep it with
any copy). *Use:* end-to-end smoke test; loader `digiklausur`. *Note:* single grader and a coarse
scale, so agreement figures are optimistic.

**SAF, Short Answer Feedback.** Filighera, Ochs, Steuer and Tregel, ACL 2022,
<https://aclanthology.org/2022.acl-long.587/>, <https://github.com/SebOchs/SAF>. Communication-networks
answers with a score, elaborated feedback and a reference answer. *Licence:* repository code MIT
(Copyright 2021 Sebastian Ochs, Anna Filighera); the data are released under CC BY 4.0 on Hugging
Face (to be re-checked against the dataset card before redistribution). *Use:* the only source of
human feedback text, so it grounds feedback style and the feedback judge; loader `saf`.

**Mohler et al. 2011.** Mohler, Bunescu and Mihalcea, "Learning to Grade Short Answer Questions
using Semantic Similarity Measures and Dependency Graph Alignments", ACL 2011,
<https://aclanthology.org/P11-1076/>. Data-structures course, about 2,200 answers, marks 0 to 5 from
two graders. *Licence:* CC BY 4.0 on the Hugging Face mirror used by the downloader. *Use:*
comparison with published short-answer grading numbers; loader `mohler`. Machine translations of a
sample (Hindi, Bengali) are derivative works and carry the same attribution.

**ScAA.** Agarwal, Gupta and Baghel (Pratham Education Foundation), "ScAA: A Dataset for Automated
Short Answer Grading of Children's Free-text Answers in Hindi and Marathi", ICON 2020. 10,988 Hindi
and 1,955 Marathi answers to 32 science questions, correct or incorrect. *Licence:* CC BY-NC-SA 4.0
(non-commercial, share-alike). *Use:* the only grading set for Hindi and Marathi found; loaders
`scaa_hindi`, `scaa_marathi`. Research use only.

### 4.2 Benchmark-only datasets (never tuned on)

**EngSAF.** Aggarwal et al., "'I understand why I got this grade': Automatic Short Answer Grading
(ASAG) with Feedback", <https://arxiv.org/abs/2407.12818>. Engineering exam answers, marks 0 to 2.
Obtained from the Hugging Face copy by Ismael Mousa. *Licence:* Apache-2.0 per that dataset card.
*Use:* final, held-out comparison only; loader `engsaf`.

**RiceChem.** Sonkar et al., "Automated Long Answer Grading with RiceChem Dataset",
<https://arxiv.org/abs/2404.14316>, <https://github.com/luffycodes/Automated-Long-Answer-Grading>.
College chemistry long answers (4 questions) with per-criterion human labels. *Licence:* none
stated; access is granted by the authors on request through the form linked in their repository.
**This project never distributes any part of it.** Request it yourself, place the CSV files where
`src/autograde/datasets/ricechem.py` looks (`find_folder`), and use loader `ricechem`. Only four
questions exist, so use it for testing, not tuning.

**ProcessBench.** Zheng et al., "ProcessBench: Identifying Process Errors in Mathematical
Reasoning", <https://huggingface.co/datasets/Qwen/ProcessBench>. Model-written solutions with the
first wrong step labelled. *Licence:* Apache-2.0. *Use:* checks that verification finds step errors;
loaders `processbench`, `processbench_hard`.

**IMO-GradingBench.** Olympiad proofs graded 0 to 7 by humans with grading guidelines, from the
Hugging Face release `Hwilner/imo-gradingbench`. *Licence:* CC BY per the release. *Use:* hardest
marking case; loader `imo_grading`.

**SemEval-2013 Task 7 (SciEntsBank).** Dzikovska et al., SemEval-2013 Task 7, via the community
mirror `Spal09/sem_eval_2013_task_7`. School science, one to two sentence answers, five-way labels.
*Licence:* Creative Commons (exact variant not verified). *Use:* literature comparison;
loader `scientsbank`.

**ASAP-SAS.** The Hewlett Foundation Automated Student Assessment Prize, short answer scoring,
<https://www.kaggle.com/c/asap-sas>. Ten prompts, scores 0 to 3. *Licence:* Kaggle competition
rules apply. *Use:* literature comparison; loader `asap_sas`.

**ASAP/AES 2.0 essays.** Learning Agency Lab, Automated Essay Scoring 2.0, via the Hugging Face
mirror `tasksource/AES2-essay-scoring`. Persuasive essays scored 1 to 6. *Licence:* CC BY-NC.
*Use:* non-STEM stress test; loader `aes2`. Non-commercial only.

### 4.3 Other datasets

**SciBench.** Wang et al., "SciBench: Evaluating College-Level Scientific Problem-Solving Abilities
of Large Language Models", <https://github.com/mandyyyyii/scibench>. College physics, chemistry and
maths problems with worked solutions. *Licence:* MIT. *Use:* question pool and category examples.

**MathDial.** Macina et al., ETH NLPED, <https://github.com/eth-nlped/mathdial>. Tutoring dialogues
with simulated student errors and the teacher's note on the confusion. *Licence:* CC BY-SA 4.0:
anything derived from it, including committed samples, must be shared under the same licence.
*Use:* misconception-aware feedback tests. The students are simulated, not real.

**IELTS essays with examiner feedback.** Hugging Face `chillies/IELTS_essay_human_feedback`.
*Licence:* not verified; do not redistribute. *Use:* feedback-style checks on essays.

**EDU-CIRCUIT-HW.** Georgia Tech Learning Innovation, <https://doi.org/10.35090/gatech/81252>,
paper <https://arxiv.org/abs/2602.00095>, code
<https://github.com/gt-learning-innovation/CIRCUIT_EDU_HW_ACL>. Handwritten circuit-analysis
homework with TA labels and rubric outputs. *Licence:* code Apache-2.0; the data licence is not
stated and problem statements are withheld by the authors for copyright reasons. *Use:* only the
tune and validate students are loaded; the remaining students are a sealed benchmark whose files are
never fetched. Loader `circuit_hw`.

**Digitised student examination papers.** Dinesh K P, "A Dataset of Digitized Student Examination
Papers, Answer Keys, and Manual Evaluations for Automated Grading Research", Mendeley Data (id
`sf3kvjwknt`). Fifty students, a Data Science exam. *Licence:* CC BY 4.0. *Use:* reading handwritten
sheets; only a tune and a validate subset is downloaded.

**IIIT Indic handwritten words.** CVIT, IIIT Hyderabad,
<https://cvit.iiit.ac.in/images/datasets/indic_handwritten/>. Handwritten word images for Hindi,
Tamil and Bengali. *Licence:* see the source site. *Use:* checking that OCR readers keep Indic
spelling.

## 5. Material made by this project

- `data/OCR_Dataset/` and `data/raw/faithful/`: handwriting test pages and generated test images
  used to compare OCR readers. Answer keys in them were written with a language model and checked
  against the teacher's totals where available. Provenance of each page must be confirmed before
  any of it is published.
- Translations and perturbed answers (`data/raw/translated/`, robustness and stress sets) are
  derived from the datasets above and keep their licences and attribution.

## 6. Excluded

Private course material, for example the ME5309 question paper, rubric and answer sheets, is not
distributed on any branch.

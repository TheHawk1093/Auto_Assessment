# evaluation/

Measures how good the grader is. Nothing here is needed to mark an exam.

**Agreement with a person**

- `metrics.py`: pure functions for exact agreement, agreement within one mark, quadratic weighted
  kappa (QWK) and bias.
- `criteria.py`: does the grader tick the same rubric criteria as the teacher?
- `calibrate.py`: fits the settings for a dataset from a few teacher-marked answers.
- `sensitivity.py`: how far did the marks move between two runs?
- `experiments.py`: adds each run to `experiments/log.jsonl` and rebuilds `experiments/RESULTS.md`.

**Tests of the grader itself.** The methods are described in `docs/DESIGN.md`.

| File | The question it answers |
|---|---|
| `stress.py` | For answers built so that the right mark is known, does the grader get it right? |
| `robustness.py` | If an answer is reworded or respelled but means the same, do the marks stay the same? |
| `compliance.py` | Do marks and feedback change with the strictness level? |
| `revision.py` and `transfer.py` | Does the feedback help a student improve, and does it teach the idea rather than only the answer? |
| `feedback_ab.py`, `judge.py` and `judge_check.py` | Is feedback built from the marking better than feedback written from the answer alone, and is the judge reliable? |
| `voting.py` and `cascade.py` | How steady is the grader, and do voting or a second model help? |

These tests work on finished runs or on a model client, so the unit tests use the scripted fake
models in `tests/fakes.py`.

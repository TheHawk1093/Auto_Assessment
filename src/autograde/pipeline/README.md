# pipeline/

The marking steps. Code does the arithmetic and the checks. The AI model only makes judgements.

| Step | File | What it guarantees |
|---|---|---|
| Scheme | `rubric.py` | One scheme per question, written once and saved in `output/rubrics/`. It is tested first: the model answer must score full marks and a blank answer must score zero |
| Code checks | `checks.py`, `objective.py`, `numeric.py`, `codecheck.py`, `codetests.py`, `figure.py`, `sandbox.py` | Multiple choice, numbers with units and tolerance, and code syntax and tests are decided by fixed rules, not by the AI |
| Read | `read.py` | A first pass over the answer on its own, before it is compared with the scheme |
| Grade | `grade.py` | A verdict on every scheme point, each backed by a quote from the answer |
| Verify | `verify.py` | Makes no AI calls. It checks that each quote is in the answer, that marks add up and that limits hold. A failed check means one retry, then a repair |
| Feedback | `feedback.py` | Written only from the checked marking, for every answer that lost marks |
| Run | `run.py` | Runs all of the above over many answers at once, and resumes an interrupted run |

Optional extras:

- `cascade.py`: a cheap model marks first, and a stronger model marks again only the answers the
  first one was unsure about.
- `vote.py`: marks the same answer several times and combines the verdicts.
- `review.py`: lists the answers that are worth a person's attention.
- `levels.py`: the strictness levels.
- `rescore.py`: recalculates marks from saved verdicts with a different rule. It needs no AI calls.
- `baseline.py`: a one-prompt grader, used as the simple comparison for every other design.

Which prompt a step uses is chosen by switches in `PipelineConfig` (in `config.py`). So changing
behaviour usually means adding a prompt file and a switch, not adding a new code path.

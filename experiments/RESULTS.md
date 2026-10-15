# Experiment results

Generated from `experiments/log.jsonl`. Do not edit. Scores are against the teacher's marks.
Error = average gap as a share of total marks (lower is better). Bias below 0 means stricter than the teacher.
▲ better, ▼ worse. Compare only rows on the same sample.

| Time | Variant | Run | Sample | Mode | Error | vs base | vs prev | Bias | Correl. | QWK | Flagged | Cost $ | Prompts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-15 22:49 | baseline | dk_baseline | digiklausur/dev/n24/seed0 | baseline | 0.217 | - | - | -0.123 | 0.78 | 0.63 | 0% | 0.14 | f6e7059c |
| 2026-10-15 22:50 | v0-citations | dk_pipeline | digiklausur/dev/n24/seed0 | pipeline | 0.203 | ▲ -0.014 | - | -0.167 | 0.67 | 0.54 | 8% | 0.70 | f6e7059c |

## Variants

- **baseline**: One prompt: question, model answer, student answer -> mark. Floor every variant must beat.. Settings: `{"rubric_selftest": true, "grade_retries": 1, "max_workers": 4}`
- **v0-citations**: Generated scheme, per-point marking with quotes, quote check zeroes unsupported credit, separate feedback call.. Settings: `{"rubric_selftest": true, "grade_retries": 1, "max_workers": 4}`

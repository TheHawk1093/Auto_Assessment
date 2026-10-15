# Experiment results

Generated from `experiments/log.jsonl`. Do not edit.
Scores are against the teacher's marks.
Error = average gap as a share of total marks (lower is better). Bias below 0 means stricter than the teacher.
▲ better, ▼ worse. Compare only rows on the same sample.

| Time | Variant | Run | Sample | Mode | Error | vs base | vs prev | Bias | Correl. | QWK | Flagged | Cost $ | Prompts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-15 22:49 | baseline | dk_baseline | digiklausur/dev/n24/seed0 | baseline | 0.217 | - | - | -0.123 | 0.78 | 0.63 | 0% | 0.14 | f6e7059c |
| 2026-10-15 22:50 | v0-citations | dk_pipeline | digiklausur/dev/n24/seed0 | pipeline | 0.203 | ▲ -0.014 | - | -0.167 | 0.67 | 0.54 | 8% | 0.70 | f6e7059c |
| 2026-10-15 23:01 | baseline | dk_s1_baseline | digiklausur/dev/n24/seed1 | baseline | 0.200 | - | - | -0.092 | 0.76 | 0.65 | 0% | 0.25 | 7ce2dafe |
| 2026-10-15 23:05 | v1-read-essence | dk_s1_v1 | digiklausur/dev/n24/seed1 | pipeline | 0.174 | ▲ -0.026 | - | -0.143 | 0.83 | 0.74 | 4% | 1.04 | 7ce2dafe |
| 2026-10-15 23:07 | baseline | saf_s0_baseline | saf/dev/n24/seed0 | baseline | 0.112 | - | - | -0.090 | 0.92 | 0.85 | 0% | 0.22 | 7ce2dafe |
| 2026-10-15 23:11 | v1-read-essence | saf_s0_v1 | saf/dev/n24/seed0 | pipeline | 0.081 | ▲ -0.031 | - | -0.050 | 0.96 | 0.92 | 0% | 1.37 | 7ce2dafe |
| 2026-10-15 23:12 | baseline | mohler_s0_baseline | mohler/dev/n24/seed0 | baseline | 0.225 | - | - | -0.225 | 0.81 | 0.51 | 0% | 0.19 | 7ce2dafe |

## Variants

- **baseline**: One prompt: question, model answer, student answer -> mark. Floor every variant must beat. Settings: `{"rubric_selftest": true, "grade_retries": 1, "max_workers": 4}`
- **v0-citations**: Generated scheme, per-point marking with quotes, quote check zeroes unsupported credit, separate feedback call. Settings: `{"rubric_selftest": true, "grade_retries": 1, "max_workers": 4}`
- **v1-read-essence**: Read answer first, then mark; essence-based policy; quotes advisory (flag), not removed. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "rubric_variant": "generated", "grade_retries": 1, "max_workers": 4}`

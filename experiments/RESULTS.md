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
| 2026-10-15 23:18 | v1-read-essence | mohler_s0_v1 | mohler/dev/n24/seed0 | pipeline | 0.252 | ▼ +0.027 | - | -0.235 | 0.80 | 0.47 | 12% | 1.46 | 7ce2dafe |
| 2026-10-15 23:21 | v2a-partial0.9 | dk_s1_v2a | digiklausur/dev/n24/seed1 | pipeline | 0.098 | ▲ -0.102 | ▲ -0.076 | -0.020 | 0.89 | 0.88 | 100% | 0.00 | 286f1adf |
| 2026-10-15 23:21 | v2a-partial0.9 | saf_s0_v2a | saf/dev/n24/seed0 | pipeline | 0.057 | ▲ -0.056 | ▲ -0.025 | 0.039 | 0.97 | 0.94 | 100% | 0.00 | 286f1adf |
| 2026-10-15 23:21 | v2a-partial0.9 | mohler_s0_v2a | mohler/dev/n24/seed0 | pipeline | 0.187 | ▲ -0.038 | ▲ -0.065 | -0.157 | 0.84 | 0.63 | 100% | 0.00 | 286f1adf |
| 2026-10-15 23:26 | v2b-sized-scheme | dk_s1_v2b | digiklausur/dev/n24/seed1 | pipeline | 0.098 | ▲ -0.102 | ▲ -0.001 | 0.006 | 0.86 | 0.84 | 4% | 1.23 | 286f1adf |
| 2026-10-15 23:29 | v2b-sized-scheme | saf_s0_v2b | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | ▼ +0.004 | 0.040 | 0.96 | 0.94 | 0% | 1.28 | 286f1adf |
| 2026-10-15 23:33 | v2b-sized-scheme | mohler_s0_v2b | mohler/dev/n24/seed0 | pipeline | 0.155 | ▲ -0.070 | ▲ -0.032 | -0.130 | 0.85 | 0.63 | 8% | 1.28 | 286f1adf |
| 2026-10-15 23:36 | v2b-sized-scheme | dk_s0_v2b | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | ▲ -0.134 | -0.027 | 0.90 | 0.92 | 0% | 0.96 | 286f1adf |
| 2026-10-15 23:47 | v3-why-sized2 | mohler_s0_v3 | mohler/dev/n24/seed0 | pipeline | 0.192 | ▲ -0.033 | ▼ +0.036 | -0.162 | 0.85 | 0.62 | 0% | 1.32 | bb2e9f90 |
| 2026-10-15 23:51 | v3-why-sized2 | dk_s0_v3 | digiklausur/dev/n24/seed0 | pipeline | 0.127 | ▲ -0.090 | ▼ +0.058 | -0.048 | 0.80 | 0.81 | 4% | 1.17 | bb2e9f90 |
| 2026-10-15 23:54 | v3-why-sized2 | saf_s0_v3 | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.97 | 0.94 | 0% | 1.27 | bb2e9f90 |
| 2026-10-16 00:10 | model-haiku | dk_s0_m_haiku | digiklausur/dev/n24/seed0 | pipeline | 0.106 | ▲ -0.110 | ▲ -0.021 | -0.031 | 0.83 | 0.83 | 12% | 0.10 | bb2e9f90 |
| 2026-10-16 00:14 | model-sonnet_low | dk_s0_m_sonnet_low | digiklausur/dev/n24/seed0 | pipeline | 0.071 | ▲ -0.146 | ▲ -0.035 | -0.029 | 0.90 | 0.92 | 4% | 1.12 | bb2e9f90 |
| 2026-10-16 00:17 | model-sonnet_high | dk_s0_m_sonnet_high | digiklausur/dev/n24/seed0 | pipeline | 0.110 | ▲ -0.106 | ▼ +0.040 | -0.069 | 0.83 | 0.83 | 4% | 1.23 | bb2e9f90 |
| 2026-10-16 00:21 | model-opus_medium | dk_s0_m_opus_medium | digiklausur/dev/n24/seed0 | pipeline | 0.089 | ▲ -0.128 | ▲ -0.022 | -0.018 | 0.86 | 0.85 | 0% | 2.90 | bb2e9f90 |
| 2026-10-16 00:54 | feedback-standard | dk_s0_fb_standard | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | ▲ -0.020 | -0.027 | 0.90 | 0.92 | 0% | 0.33 | 55478d58 |
| 2026-10-16 00:55 | feedback-hints | dk_s0_fb_hints | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | = | -0.027 | 0.90 | 0.92 | 0% | 0.33 | 55478d58 |
| 2026-10-16 00:57 | feedback-critique | dk_s0_fb_critique | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | = | -0.027 | 0.90 | 0.92 | 0% | 0.62 | 55478d58 |
| 2026-10-17 23:11 | v4-votes3 | dk_s0_votes3 | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | = | -0.027 | 0.90 | 0.92 | 12% | 1.60 | 0dc1c2c8 |
| 2026-10-17 23:15 | v4-votes3 | saf_s0_votes3 | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.96 | 0.94 | 0% | 1.44 | 0dc1c2c8 |
| 2026-10-17 23:17 | baseline | engsaf_s0_baseline | engsaf/test/n60/seed0 | baseline | 0.179 | - | - | -0.096 | 0.76 | 0.73 | 0% | 0.54 | 0dc1c2c8 |
| 2026-10-17 23:27 | v2b-sized-scheme | engsaf_s0_v2b | engsaf/test/n60/seed0 | pipeline | 0.158 | ▲ -0.021 | - | 0.027 | 0.78 | 0.77 | 3% | 3.54 | 0dc1c2c8 |
| 2026-10-17 23:37 | v2b-mask30 | dk_s0_mask30 | digiklausur/dev/n24/seed0 | pipeline | 0.100 | ▲ -0.117 | ▼ +0.031 | -0.063 | 0.87 | 0.86 | 100% | 1.49 | 0dc1c2c8 |

## Variants

- **baseline**: One prompt: question, model answer, student answer -> mark. Floor every variant must beat. Settings: `{"rubric_selftest": true, "grade_retries": 1, "max_workers": 4}`
- **v0-citations**: Generated scheme, per-point marking with quotes, quote check zeroes unsupported credit, separate feedback call. Settings: `{"rubric_selftest": true, "grade_retries": 1, "max_workers": 4}`
- **v1-read-essence**: Read answer first, then mark; essence-based policy; quotes advisory (flag), not removed. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "rubric_variant": "generated", "grade_retries": 1, "max_workers": 4}`
- **v2a-partial0.9**: Same verdicts as v1, priced in code: partial = 0.9 of a point. No model calls. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "rubric_variant": "generated", "grade_retries": 1, "max_workers": 4, "mark_rule": "status", "partial_weight": 0.9, "rescored_from": "dk_s1_v1"}`
- **v2b-sized-scheme**: v2a plus schemes sized to the model answer (no invented sub-points). Full re-run. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4}`
- **v3-why-sized2**: feedback explains why; scheme folds terminology. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized2", "grade_retries": 1, "max_workers": 4}`
- **model-haiku**: same pipeline, grader model/effort = haiku. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4}`
- **model-sonnet_low**: same pipeline, grader model/effort = sonnet_low. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4}`
- **model-sonnet_high**: same pipeline, grader model/effort = sonnet_high. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4}`
- **model-opus_medium**: same pipeline, grader model/effort = opus_medium. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4}`
- **feedback-standard**: same marks as dk_s0_v2b, feedback=standard. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4, "feedback_variant": "standard", "refeedback_from": "dk_s0_v2b"}`
- **feedback-hints**: same marks as dk_s0_v2b, feedback=hints. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4, "feedback_variant": "hints", "refeedback_from": "dk_s0_v2b"}`
- **feedback-critique**: same marks as dk_s0_v2b, feedback=critique. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4, "feedback_variant": "critique", "refeedback_from": "dk_s0_v2b"}`
- **v4-votes3**: mark 3 times, majority per point. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 3, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **v2b-mask30**: 30 percent of model answer words blanked. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`

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
| 2026-10-17 23:40 | v2b-short50 | dk_s0_short50 | digiklausur/dev/n24/seed0 | pipeline | 0.179 | ▲ -0.037 | ▼ +0.079 | 0.054 | 0.66 | 0.63 | 4% | 1.16 | 0dc1c2c8 |
| 2026-10-17 23:41 | feedback-formal | dk_s0_fb_formal | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | ▲ -0.110 | -0.027 | 0.90 | 0.92 | 0% | 0.33 | 0dc1c2c8 |
| 2026-10-17 23:44 | feedback-best3 | dk_s0_fb_best3 | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | = | -0.027 | 0.90 | 0.92 | 0% | 1.28 | 0dc1c2c8 |
| 2026-10-18 00:14 | v5-form-gate | dk_s0_v5 | digiklausur/dev/n24/seed0 | pipeline | 0.071 | ▲ -0.146 | ▼ +0.002 | -0.029 | 0.90 | 0.92 | 0% | 0.93 | 55a3b874 |
| 2026-10-18 00:16 | v5-form-gate | saf_s0_v5 | saf/dev/n24/seed0 | pipeline | 0.106 | ▲ -0.006 | ▼ +0.046 | -0.006 | 0.91 | 0.89 | 21% | 0.91 | 55a3b874 |
| 2026-10-18 00:19 | v5-form-gate | mohler_s0_v5 | mohler/dev/n24/seed0 | pipeline | 0.183 | ▲ -0.042 | ▲ -0.009 | -0.158 | 0.87 | 0.63 | 8% | 0.79 | 55a3b874 |
| 2026-10-18 00:25 | v5-form-gate | engsaf_s0_v5 | engsaf/test/n60/seed0 | pipeline | 0.163 | ▲ -0.017 | ▼ +0.004 | -0.009 | 0.77 | 0.76 | 8% | 2.13 | 55a3b874 |
| 2026-10-18 00:28 | v5b-form-gate-lists | saf_s0_v5b | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | ▲ -0.046 | 0.040 | 0.96 | 0.94 | 21% | 0.95 | f53c937e |
| 2026-10-18 13:19 | v6-review | dk_s0_v6 | digiklausur/dev/n24/seed0 | pipeline | 0.088 | ▲ -0.129 | ▼ +0.017 | -0.008 | 0.86 | 0.87 | 29% | 0.95 | f53c937e |
| 2026-10-18 13:26 | v6-review | mohler_s0_v6 | mohler/dev/n24/seed0 | pipeline | 0.174 | ▲ -0.051 | ▲ -0.009 | -0.149 | 0.82 | 0.59 | 25% | 0.79 | f53c937e |
| 2026-10-18 13:41 | v6-review | engsaf_s0_v6 | engsaf/test/n60/seed0 | pipeline | 0.158 | ▲ -0.022 | ▲ -0.005 | 0.029 | 0.78 | 0.77 | 17% | 2.14 | f53c937e |
| 2026-10-19 16:13 | feedback-brief | dk_s0_fb_brief | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | ▲ -0.019 | -0.027 | 0.90 | 0.92 | 0% | 0.33 | 0ec7c5eb |
| 2026-10-19 16:14 | feedback-detailed | dk_s0_fb_detailed | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | = | -0.027 | 0.90 | 0.92 | 0% | 0.36 | 0ec7c5eb |
| 2026-10-19 16:15 | feedback-coach | dk_s0_fb_coach | digiklausur/dev/n24/seed0 | pipeline | 0.069 | ▲ -0.148 | = | -0.027 | 0.90 | 0.92 | 0% | 0.30 | 48bc24b0 |
| 2026-10-19 16:16 | feedback-standard | saf_s0_fb_standard | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.96 | 0.94 | 0% | 0.31 | 48bc24b0 |
| 2026-10-19 16:17 | feedback-hints | saf_s0_fb_hints | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.96 | 0.94 | 0% | 0.32 | 48bc24b0 |
| 2026-10-19 16:20 | feedback-critique | saf_s0_fb_critique | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.96 | 0.94 | 0% | 0.63 | 48bc24b0 |
| 2026-10-19 16:22 | feedback-formal | saf_s0_fb_formal | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.96 | 0.94 | 0% | 0.33 | 48bc24b0 |
| 2026-10-19 16:23 | feedback-brief | saf_s0_fb_brief | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.96 | 0.94 | 0% | 0.29 | 48bc24b0 |
| 2026-10-19 16:24 | feedback-detailed | saf_s0_fb_detailed | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.96 | 0.94 | 0% | 0.36 | 48bc24b0 |
| 2026-10-19 16:26 | feedback-coach | saf_s0_fb_coach | saf/dev/n24/seed0 | pipeline | 0.060 | ▲ -0.052 | = | 0.040 | 0.96 | 0.94 | 0% | 0.33 | 48bc24b0 |
| 2026-10-22 16:01 | baseline | rice_s0_baseline | ricechem/test/n72/seed0 | baseline | 0.154 | - | - | -0.065 | 0.81 | 0.77 | 0% | 0.90 | 110a77f2 |
| 2026-10-22 16:11 | official-rubric | rice_s0_official | ricechem/test/n72/seed0 | pipeline | 0.150 | ▲ -0.004 | - | 0.116 | 0.82 | 0.74 | 18% | 3.78 | 110a77f2 |
| 2026-10-22 16:22 | generated-rubric | rice_s0_sized | ricechem/test/n72/seed0 | pipeline | 0.158 | ▼ +0.004 | ▼ +0.008 | 0.113 | 0.80 | 0.73 | 100% | 3.92 | 110a77f2 |
| 2026-10-22 16:31 | rubric-lenient | rice_s0_lenient | ricechem/test/n72/seed0 | pipeline | 0.190 | ▼ +0.036 | ▼ +0.032 | 0.181 | 0.79 | 0.62 | 11% | 3.47 | 110a77f2 |
| 2026-10-22 16:40 | rubric-moderate | rice_s0_moderate | ricechem/test/n72/seed0 | pipeline | 0.149 | ▲ -0.005 | ▲ -0.040 | 0.052 | 0.80 | 0.71 | 12% | 3.50 | 110a77f2 |
| 2026-10-22 16:53 | rubric-harsh | rice_s0_harsh | ricechem/test/n72/seed0 | pipeline | 0.174 | ▼ +0.020 | ▼ +0.024 | -0.142 | 0.89 | 0.78 | 36% | 4.15 | 110a77f2 |
| 2026-10-25 00:20 | poc-pipeline | poc_digiklausur_pipeline | digiklausur/dev/n6/seed0 | pipeline | 0.092 | - | - | -0.092 | - | 0.00 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:20 | poc-baseline | poc_digiklausur_baseline | digiklausur/dev/n6/seed0 | baseline | 0.292 | - | - | -0.292 | - | 0.00 | 0% | 0.01 | 027fb978 |
| 2026-10-25 00:22 | poc-pipeline | poc_digiklausur_pipeline | digiklausur/dev/n8/seed0 | pipeline | 0.122 | - | - | -0.122 | - | 0.00 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:22 | poc-baseline | poc_digiklausur_baseline | digiklausur/dev/n8/seed0 | baseline | 0.250 | - | - | -0.250 | - | 0.00 | 0% | 0.01 | 027fb978 |
| 2026-10-25 00:24 | poc-pipeline | poc_saf_pipeline | saf/dev/n8/seed0 | pipeline | 0.150 | - | - | -0.150 | 0.94 | 0.81 | 62% | 0.03 | 027fb978 |
| 2026-10-25 00:24 | poc-baseline | poc_saf_baseline | saf/dev/n8/seed0 | baseline | 0.181 | - | - | -0.181 | 0.88 | 0.81 | 0% | 0.01 | 027fb978 |
| 2026-10-25 00:26 | poc-pipeline | poc_mohler_pipeline | mohler/dev/n8/seed0 | pipeline | 0.287 | - | - | -0.277 | 0.91 | 0.56 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:26 | poc-baseline | poc_mohler_baseline | mohler/dev/n8/seed0 | baseline | 0.312 | - | - | -0.312 | 0.82 | 0.36 | 0% | 0.01 | 027fb978 |
| 2026-10-25 00:28 | poc-pipeline | poc_engsaf_pipeline | engsaf/dev/n8/seed0 | pipeline | 0.269 | - | - | -0.144 | 0.51 | 0.44 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:28 | poc-baseline | poc_engsaf_baseline | engsaf/dev/n8/seed0 | baseline | 0.188 | - | - | 0.000 | 0.72 | 0.71 | 0% | 0.01 | 027fb978 |
| 2026-10-25 00:30 | poc-pipeline | poc_ricechem_pipeline | ricechem/dev/n8/seed0 | pipeline | 0.094 | - | - | 0.031 | 0.91 | 0.92 | 38% | 0.03 | 027fb978 |
| 2026-10-25 00:30 | poc-baseline | poc_ricechem_baseline | ricechem/dev/n8/seed0 | baseline | 0.133 | - | - | -0.008 | 0.78 | 0.76 | 0% | 0.01 | 027fb978 |
| 2026-10-25 00:42 | poc-lenient | poc_digiklausur_lenient | digiklausur/dev/n8/seed0 | pipeline | 0.219 | ▲ -0.031 | ▼ +0.097 | -0.219 | - | 0.00 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:44 | poc-lenient | poc_saf_lenient | saf/dev/n8/seed0 | pipeline | 0.062 | ▲ -0.119 | ▲ -0.087 | -0.062 | 0.98 | 0.96 | 38% | 0.03 | 027fb978 |
| 2026-10-25 00:45 | poc-lenient | poc_mohler_lenient | mohler/dev/n8/seed0 | pipeline | 0.213 | ▲ -0.100 | ▲ -0.075 | -0.037 | 0.27 | 0.29 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:47 | poc-lenient | poc_engsaf_lenient | engsaf/dev/n8/seed0 | pipeline | 0.188 | = | ▲ -0.081 | -0.062 | 0.62 | 0.62 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:49 | poc-lenient | poc_ricechem_lenient | ricechem/dev/n8/seed0 | pipeline | 0.109 | ▲ -0.023 | ▼ +0.016 | 0.109 | 0.83 | 0.84 | 12% | 0.04 | 027fb978 |
| 2026-10-25 00:51 | poc-moderate | poc_digiklausur_moderate | digiklausur/dev/n8/seed0 | pipeline | 0.269 | ▼ +0.019 | ▼ +0.050 | -0.269 | - | 0.00 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:53 | poc-moderate | poc_saf_moderate | saf/dev/n8/seed0 | pipeline | 0.103 | ▲ -0.078 | ▼ +0.041 | -0.103 | 0.94 | 0.90 | 50% | 0.03 | 027fb978 |
| 2026-10-25 00:55 | poc-moderate | poc_mohler_moderate | mohler/dev/n8/seed0 | pipeline | 0.255 | ▲ -0.057 | ▼ +0.043 | -0.230 | 0.73 | 0.40 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:57 | poc-moderate | poc_engsaf_moderate | engsaf/dev/n8/seed0 | pipeline | 0.290 | ▼ +0.103 | ▼ +0.103 | -0.165 | 0.59 | 0.54 | 0% | 0.03 | 027fb978 |
| 2026-10-25 00:59 | poc-moderate | poc_ricechem_moderate | ricechem/dev/n8/seed0 | pipeline | 0.125 | ▲ -0.008 | ▼ +0.016 | 0.000 | 0.76 | 0.48 | 12% | 0.04 | 027fb978 |
| 2026-10-25 01:02 | poc-harsh | poc_digiklausur_harsh | digiklausur/dev/n8/seed0 | pipeline | 0.662 | ▼ +0.412 | ▼ +0.394 | -0.662 | - | 0.00 | 12% | 0.04 | 027fb978 |
| 2026-10-25 01:04 | poc-harsh | poc_saf_harsh | saf/dev/n8/seed0 | pipeline | 0.163 | ▲ -0.019 | ▼ +0.059 | -0.163 | 0.91 | 0.75 | 50% | 0.03 | 027fb978 |
| 2026-10-25 01:06 | poc-harsh | poc_mohler_harsh | mohler/dev/n8/seed0 | pipeline | 0.412 | ▼ +0.100 | ▼ +0.157 | -0.412 | 0.85 | 0.36 | 0% | 0.03 | 027fb978 |
| 2026-10-25 01:07 | poc-harsh | poc_engsaf_harsh | engsaf/dev/n8/seed0 | pipeline | 0.370 | ▼ +0.182 | ▼ +0.080 | -0.245 | 0.42 | 0.30 | 0% | 0.03 | 027fb978 |
| 2026-10-25 01:09 | poc-harsh | poc_ricechem_harsh | ricechem/dev/n8/seed0 | pipeline | 0.227 | ▼ +0.094 | ▼ +0.102 | -0.148 | 0.56 | 0.35 | 0% | 0.04 | 027fb978 |
| 2026-10-25 16:28 | poc-pipeline | poc_saf_pipeline | saf/dev/n8/seed0 | pipeline | 0.150 | ▲ -0.031 | ▲ -0.013 | -0.150 | 0.94 | 0.81 | 62% | 0.00 | 4834e514 |
| 2026-10-25 16:30 | poc-pipeline | poc_saf_pipeline | saf/dev/n8/seed0 | pipeline | 0.088 | ▲ -0.094 | ▲ -0.062 | -0.088 | 0.96 | 0.90 | 62% | 0.03 | 4834e514 |
| 2026-10-25 19:21 | loop0 | loop0_digiklausur | digiklausur/dev/n20/seed1 | pipeline | 0.151 | - | - | 0.016 | 0.74 | 0.70 | 5% | 0.04 | b9be9f4d |
| 2026-10-25 19:22 | loop0 | loop0_saf | saf/dev/n20/seed1 | pipeline | 0.146 | - | - | 0.036 | 0.85 | 0.79 | 25% | 0.04 | b9be9f4d |

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
- **v2b-short50**: model answer cut to first half. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **feedback-formal**: formal examiner register. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4, "feedback_variant": "formal", "refeedback_from": "dk_s0_v2b"}`
- **feedback-best3**: 3 drafts, checks, pick best. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4, "feedback_variant": "standard", "refeedback_from": "dk_s0_v2b"}`
- **v5-form-gate**: form gate + injection guard. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **v5b-form-gate-lists**: keyword_list only when an explanation was asked. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **v6-review**: final design + haiku second opinion flag. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 1, "second_model": "haiku", "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **feedback-brief**: same marks as dk_s0_v2b. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4, "feedback_variant": "brief", "refeedback_from": "dk_s0_v2b"}`
- **feedback-detailed**: same marks as dk_s0_v2b. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4, "feedback_variant": "detailed", "refeedback_from": "dk_s0_v2b"}`
- **feedback-coach**: same marks as dk_s0_v2b. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "grade_retries": 1, "max_workers": 4, "feedback_variant": "coach", "refeedback_from": "dk_s0_v2b"}`
- **official-rubric**: RiceChem benchmark; the dataset's own rubric. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "official", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **generated-rubric**: RiceChem benchmark; rubric written by the system from the reference. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **rubric-lenient**: RiceChem benchmark; rubric strictness lenient. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "lenient", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **rubric-moderate**: RiceChem benchmark; rubric strictness moderate. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "moderate", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **rubric-harsh**: RiceChem benchmark; rubric strictness harsh. Settings: `{"rubric_selftest": true, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "harsh", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "grade_retries": 1, "max_workers": 4}`
- **poc-pipeline**: proof of concept. Settings: `{"rubric_selftest": false, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "ocr": null, "grade_retries": 1, "max_workers": 4}`
- **poc-baseline**: proof of concept. Settings: `{"rubric_selftest": false, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "ocr": null, "grade_retries": 1, "max_workers": 4}`
- **poc-lenient**: proof of concept. Settings: `{"rubric_selftest": false, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "lenient", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "ocr": null, "grade_retries": 1, "max_workers": 4}`
- **poc-moderate**: proof of concept. Settings: `{"rubric_selftest": false, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "moderate", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "ocr": null, "grade_retries": 1, "max_workers": 4}`
- **poc-harsh**: proof of concept. Settings: `{"rubric_selftest": false, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "harsh", "feedback_variant": "standard", "votes": 1, "second_model": null, "disagree_gap": 0.15, "feedback_n": 1, "ocr": null, "grade_retries": 1, "max_workers": 4}`
- **loop0**: grader fix-the-misses round 0. Settings: `{"rubric_selftest": false, "read_first": true, "evidence_policy": "flag", "policy": "essence", "mark_rule": "status", "partial_weight": 0.9, "rubric_variant": "sized", "feedback_variant": "formal", "votes": 1, "second_model": null, "disagree_gap": 0.15, "with_feedback": false, "feedback_n": 1, "ocr": null, "grade_retries": 1, "max_workers": 6}`

# tests/

```bash
uv run pytest                      # the whole suite: offline, takes a few minutes
uv run pytest tests/test_verify.py # one file
uv run pytest --cov                # with a coverage report
```

No test uses the network or a real key. The AI model is replaced by scripted fake replies
(`fakes.py`) or by the offline `mock` backend. So when a test fails, the code changed. It cannot be
caused by an AI provider.

| Area | Files |
|---|---|
| Marking steps | `test_pipeline.py`, `test_verify.py`, `test_evidence.py`, `test_solid_rubric.py`, `test_deductions.py`, `test_followthrough.py`, `test_vote.py`, `test_cascade.py` |
| Question types | `test_objective.py`, `test_mcq_key.py`, `test_numeric.py`, `test_codetests.py`, `test_figure_*.py`, `test_kinds_pipeline.py` |
| Reading the exam files | `test_intake.py`, `test_identity.py`, `test_rules.py`, `test_counting.py` |
| Models and prompts | `test_mock_backend.py`, `test_prompts.py`, `test_pipeline_language.py` |
| Measuring the grader and datasets | `test_metrics.py`, `test_robustness.py`, `test_revision.py`, `test_judge_check.py`, `test_loaders.py`, `test_circuit_loader.py` |
| Handwriting | `test_ocr_noise.py`, `test_ocr_readers.py`, `test_faithful.py` |
| Web app | `test_app*.py` and `app_support.py` |
| Logging, git and reports | `test_logsetup.py`, `test_vcs.py`, `test_viewer.py` |

Two helpers are in `conftest.py`. It sets `AUTOGRADE_NO_FILE_LOG`, so tests never write to
`output/logs/`. It also provides the `env` fixture, which points the web app at a temporary
folder.

Tests that need downloaded datasets are skipped when the data is missing.
`test_sandbox_real.py` runs only when `AUTOGRADE_REAL_SANDBOX=1` is set.

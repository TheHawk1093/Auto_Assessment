# configs/

Settings files in YAML. Each one is loaded into `Settings` (`src/autograde/config.py`). Pass one
with the `--config` flag, **before** the command name:

```bash
autograde --config configs/exam.yaml exam ...
```

Always include the `.yaml` ending. A file that does not exist is an error.

| File | What it is for |
|---|---|
| `default.yaml` | The development baseline (Claude through the CLI). Every pipeline switch is listed and commented |
| `exam.yaml` | **The deployment config.** The model settings, and the handwriting readers: the main reader and the fallbacks, in order |
| `mock.yaml` | The offline demo and the tests. It uses the `mock` model and needs no key |
| `poc.yaml` | Development: a cheap trial on every dataset |
| `models/` | Small variants that change only the model or effort (`haiku`, `sonnet_low` and so on) |

A config has these sections:

| Section | What it sets |
|---|---|
| `llm` | The model that marks, writes schemes and writes feedback |
| `judge` | The model that scores feedback quality. Use a different provider from `llm` |
| `student` | The model that plays a student in the revision test |
| `pipeline` | The switches for each marking step |
| `ocr` | How handwriting is read: the main reader, the backups and the specialist route |
| `paths` | Where data is read from (`data/`) and where output goes (`output/runs/`, `output/rubrics/`, `output/logs/`) |

Keys never go in a config file. They come from the environment or from `.env`.

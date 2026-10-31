# cli/

The `autograde` command. The `main()` function in `__init__.py` reads the command line, loads the
YAML config, sets up logging (to the console and to `output/logs/`) and runs the chosen command.
Each module here adds its own commands through a `register(sub)` function.

Pass `--config` **before** the command name: `autograde --config configs/exam.yaml exam ...`.

| Module | Commands | What they are for |
|---|---|---|
| `exam.py` | `exam` | Mark a whole exam from its paper, answer key and answers. **This is the main command** |
| `scan.py` | `scan` | Read photographed answer sheets into text files that `exam` can mark |
| `recheck.py` | `recheck` | Mark one answer again with a note from the teacher. It only proposes a mark |
| `runs.py` | `download`, `run`, `poc`, `judge`, `report`, `rescore`, `refeedback`, `view`, `log`, `history` | Benchmark runs on public datasets, and reporting on or reworking a finished run |
| `rubrics.py` | `rubrics`, `official-rubrics`, `rubrics-md` | Write, install and export marking schemes |
| `evals.py` | `stress`, `transfer`, `revision`, `feedback-ab`, `review`, `robustness`, `judge-sheet`, `judge-agreement`, `votes`, `sensitivity`, `criteria`, `calibrate`, `cascade`, `compliance` | Tests of the grader itself |
| `pages.py` | `styles-page`, `rubrics-page`, `compare` | Build HTML pages for reading results |
| `ocr.py` | `ocr` | Read answer-sheet photos into items |
| `common.py` | | Helpers shared by the other modules |

```bash
uv run autograde --help
uv run autograde --config configs/mock.yaml exam --help
```

To add a command, create a module with a `register(sub)` function and list it in `MODULES` in
`__init__.py`. Teachers use `exam`, `scan` and `recheck`. The other commands are for measuring the
grader.

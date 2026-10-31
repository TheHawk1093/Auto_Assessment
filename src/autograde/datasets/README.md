# datasets/

Loaders that turn public grading datasets into items (one student answer each). They are used to
measure the grader. You do not need them to mark your own exam.

- `loaders.py` is the entry point. It provides `load_dataset(name, data_dir)` and
  `select(items, split, n)`. The `dev` and `test` split is made by **question**, not by student, so
  nothing tuned on a dev question is ever tested on the same question.
- `download.py` (the `autograde download` command) fetches the openly licensed datasets into
  `data/raw/`. Data that is already there is skipped.
- `scaa.py`, `circuit.py`, `ricechem.py`, `handwriting.py`, `extra.py` and `xlsx.py` each read one
  dataset. `translate.py` and `perturb.py` build test variants of a dataset.

The data itself is never committed. Licences, sources and how each dataset may be used are in
[docs/DATA_CREDITS.md](../../../docs/DATA_CREDITS.md), and the catalogue is in
[docs/DATASETS.md](../../../docs/DATASETS.md). Some datasets (RiceChem, EngSAF) are available only
on request or are for benchmarking only. Never tune on them.

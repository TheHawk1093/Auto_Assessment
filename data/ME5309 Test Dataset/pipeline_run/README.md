# ME5309 pipeline test (30 students: 15 random from b1, 15 from b2)

Sampled with seed 20261029. Scheme writer: Sonnet (from your TA rubric). Marker and feedback: Haiku, medium effort.

| File | What it is |
|---|---|
| `students/<id>.md` | Marks and feedback per question for each student. `b1_S006` = batch 1 sheet 6; `b2_S56` = batch 2 sheet 56 |
| `marks.csv` | Pipeline marks per part. `total` is out of 40 (all four questions); the best-three total is in `comparison.csv` |
| `comparison.csv` | Per student: reference and pipeline marks for each part, best-three totals (struck-out questions excluded) and the difference |
| `summary_table.md` | Accuracy table |
| `schemes.md` | The marking scheme the pipeline built from the rubric (read this first) |
| `answers/` | The text extracted from each answer PDF and given to the marker |
| `gold.json` | Reference marks used (b1: proposed scheme from the dataset; b2: its ground-truth workbook) |
| `config.yaml` | Models and switches used |

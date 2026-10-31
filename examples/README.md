# examples/

Everything you need to try the project after a fresh clone. No database is included. The web app's
data (`app_data/`: users, exams and marks) is git-ignored and is rebuilt from the code and the
files below.

| Folder | What it holds | How to use it |
|---|---|---|
| `exam_demo/` | A 4-question paper, two kinds of answer key (model answers only, or rubric only) and 3 students | The offline quick start in the main README. It needs no API key |
| `exam_kinds/` | One paper with every question type: multiple choice, numeric, code and more | `autograde exam` |
| `exam_pipeline/` | A complete exam: paper, model answer, rubric, class list, clean and messy answers, and the expected marks | The web app's "[Demo] Pipeline Test" exam, or `autograde exam` |
| `case4_coding/` | A coding exam: paper, answer key with tests, class list, 7 student zip files and the expected marks | `python -m app.services.cases seed case4` |
| `case1_printed/`, `case2_ocr/`, `case3_language/` | Builders for the other demo cases. They need public datasets in `data/raw/`, which cannot be shared here, so they work only after you download those datasets | [docs/DEMO_CASES.md](../docs/DEMO_CASES.md) |

## A web app with demo data, in three commands

```bash
uv run python -m app.services.demo seed                 # accounts, courses, students and demo exams
uv run python -m app.services.cases seed case4          # the self-contained coding exam
uv run streamlit run app/main.py
```

Every demo account uses the made-up password `demo1234`, and the administrator is `admin` /
`admin`. None of these accounts belongs to a real person. Each account's story is written in
`app_data/demo_personas.md`.

Seeding can be repeated safely. To remove all the demo data, run
`python -m app.services.demo remove`.

To move your own web app data to another computer, copy the whole `app_data/` folder. It holds
`app.db` and the exam folders. Keep it out of git.

# intake/

Turns the files a teacher already has into the items that the pipeline marks. Nothing in this
folder marks an answer.

| File | What it does |
|---|---|
| `files.py` | Reads the text out of txt, md, docx, text PDF and json files |
| `paper.py` | Turns the question paper into questions with marks. An AI model reads free text; json is used as it is |
| `reference.py` | Reads model answers and rubrics (in one file or two) and matches them to questions |
| `answers.py` | Reads student answers from typed files, a json file, or sheets read by `autograde scan` |
| `identity.py` | Reads each sheet's roll number and name, checks them against the student list, and holds back any sheet it is unsure about |
| `rules.py` | Reads exam-wide rules from the paper's instructions: working required, how part marks work, carrying an earlier mistake forward |
| `counting.py` | Handles "best N of M" questions and struck-out answers |
| `figures.py` | Finds figures in answer and reference files (a markdown image, `[figure: path]`, or a picture inside a docx) |
| `exam.py` | Joins all the parts into items, and writes `schemes.md` for the teacher to read |
| `models.py` | Describes an exam as the teacher gives it: paper, reference files and answers |

The prompts used by these steps are in `prompts/intake/`. When a rule in the documents disagrees
with a flag the teacher passed on the command line, the teacher's flag wins.

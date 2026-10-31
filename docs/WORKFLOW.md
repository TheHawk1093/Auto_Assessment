# Workflow

![How autograde works: exam files go in, marks and feedback come out](images/workflow.svg)

The diagrams in this repository are drawn by `docs/images/build_diagrams.py`. Run
`python docs/images/build_diagrams.py` to rebuild them. They are plain SVG, so they stay sharp at
any size.

## The four stages

1. **Read the files** (`intake/`). The paper, answer key and student answers become items. Each
   item holds the question, the model answer, the student's answer, the maximum mark and the
   question type. Rules written in the exam documents (working required, how part marks work,
   carrying an earlier mistake forward) are read by `intake/rules.py`. `intake/identity.py` checks
   who wrote each sheet.
2. **Write a marking scheme** (`pipeline/rubric.py`). Each question gets one scheme: points with
   marks, and optional partial-credit levels. The scheme is tested before use. The model answer
   must score full marks and a blank answer must score zero. A scheme that fails is rewritten once.
   Schemes are saved in `output/rubrics/<client>/<variant>/`.
3. **Mark each answer** (`pipeline/run.py`, several answers at a time).
   - `checks.py` settles multiple choice, numbers and code facts with fixed rules.
   - `read.py` reads the answer on its own.
   - `grade.py` gives a verdict on every scheme point, with a quote.
   - `verify.py` confirms that the quotes are real, that the marks add up and that the answer is
     in the required form. It allows one retry, then repairs the result.
   - Answers the grader is unsure about can be marked again by a stronger or second model
     (`cascade.py` and `vote.py`).
4. **Write feedback and save the results** (`pipeline/feedback.py` and `viewer/`). Feedback is
   written only from the checked marking. The output is `schemes.md`, `marks.csv`,
   `students/*.md` and `report.html`.

Every call to an AI model goes through `llm/` (`ask(system, user, PydanticModel)`). A backend can
therefore be swapped, or replaced by the offline `mock`, without changing any step.

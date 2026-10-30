ME 5309 ANSWER-SHEET GRADING DATASET
====================================

Contents
- answer_sheets/: 60 anonymous answer booklets (answer_001.pdf through answer_060.pdf).
- latex_sources/: corresponding editable LaTeX sources.
- subpart_grading_reference.csv: expected marks, attempt status, answer-variant labels, error annotations, and feedback by subpart.
- student_summary.csv: question scores and best-three total; no names or student profiles.
- student_feedback.csv: feedback reference without names or student profiles.
- proposed_reference_answer_key.txt: proposed solution reference.

Answer-sheet design
- Student names, IDs, performance profiles, and dataset/sample labels are not printed in the answer booklets.
- Unattempted subparts are left blank rather than labelled as unanswered. Explicit statements such as “I don't know” or “I could not finish” are removed; any mathematical work preceding them is retained.
- Attempted responses have more intermediate arithmetic and working where this can be expanded without changing the intended answer variant. Final-answer-only cases remain final-answer-only so the rubric rule can still be tested.
- Scripts retain varied correctness, incomplete derivations, conceptual mistakes, unit/sign/arithmetic errors, and uneven work across subparts.

Grading notes
- The question paper does not contain an official detailed rubric. Reference marks therefore use a proposed marking scheme and should be reviewed before treating them as gold labels.
- The exam instruction says a final numerical answer without the formula earns no credit; final-answer-only variants are scored accordingly in the reference.
- The total is based on the best three questions out of four, capped at 30.
- `student_id` in the CSV is only a neutral join key; the answer sheets themselves contain no identifying or performance metadata.

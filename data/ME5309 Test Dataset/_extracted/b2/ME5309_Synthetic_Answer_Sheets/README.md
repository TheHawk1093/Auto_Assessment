# ME 5309 Mid-Semester: synthetic answer sheets for grader testing

60 synthetic student answer sheets (PDF) with ground-truth marks, for testing an automated grading pipeline.

| Folder | Contents |
|---|---|
| `01_Question_Paper/` | The original question paper (30 marks, attempt any 3 of 4) |
| `02_Answer_Sheets/` | 60 student PDFs, `ME5309_Midsem_S01_...` to `S60_...` (batches: S01-12, S13-24, S25-36, S37-48, S49-60) |
| `03_Ground_Truth/` | `ME5309_Midsem_GroundTruth_ALL60.xlsx` (Summary, Part_Marks, Error_Log, Rubric_ModelAnswer) plus CSV exports of the same sheets |
| `04_Model_Answer/` | Full model answer script for all four questions |
| `05_Generator_Source/` | Python source used to generate the sheets (paths inside are hard-coded to the original working directories) |

## Marking conventions
- Total = best three of four question scores (10 each, 30 maximum).
- A struck-out question counts as 0, even if it would have scored higher (S04, S23, S35, S47, S59).
- Unattempted questions score 0.
- Answers with no formula or substitution earn no credit (paper instruction 5).
- 0.5 marks are deducted for missing units or fewer than 3 significant figures (instructions 6 and 7).
- Error-carried-forward credit is given where the method is right.
- The rubric was derived from the paper (none was supplied); see the `Rubric_ModelAnswer` sheet.

## Workbook sheets
- **Summary**: per-student raw and counted question marks, best-3 total (formulas), errors injected, typo counts, the pipeline test focus and the PDF path.
- **Part_Marks**: expected marks for each of the 15 parts (Q1a to Q4d).
- **Error_Log**: every deliberate mistake, its category, description and marks lost, plus blank and struck-out questions.
- **Rubric_ModelAnswer**: rubric items and model answers.

The answer sheets are typed, contain no marks, and have deliberate spelling mistakes. Velocity and acceleration are written with spacing dots (theta-dot as θ˙, theta-double-dot as θ¨) because the font would not render combining dots.

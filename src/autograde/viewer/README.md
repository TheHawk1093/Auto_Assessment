# viewer/

Builds the HTML pages that a person reads. Each page is a single self-contained file. It needs no
server and no internet, so you can open it from disk or send it by email.

| File | The page it builds |
|---|---|
| `build.py` | `report.html` for a finished run: every answer with its marks, quotes and feedback, plus the accuracy figures |
| `compare.py` | One tab per marking method, showing the same answers in each tab |
| `rubrics.py` and `rubrics_md.py` | The marking schemes for each dataset and strictness level, as a page or as markdown |
| `styles.py` | Feedback styles side by side, with measured statistics |

`autograde view --name <run>` rebuilds the `report.html` of a run in `output/runs/<name>/`.

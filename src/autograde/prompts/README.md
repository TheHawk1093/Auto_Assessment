# prompts/

Every instruction sent to an AI model is a markdown file in this folder. None is written as a
string inside the code. Changing how the system behaves is usually a matter of editing or adding
one file here.

| Folder | Used by |
|---|---|
| `rubric/` | The step that writes marking schemes (`pipeline/rubric.py`) |
| `read/` | The first pass over an answer on its own |
| `grade/` | The marker: strictness, partial credit and variants per question type |
| `feedback/` | The feedback writers and their styles |
| `intake/` | Reading papers, answer keys, answers, identities and exam-wide rules |
| `ocr/` | Reading handwritten pages |
| `checks/` | Code tests, figure descriptions and transcription |
| `language/` | Everything specific to a language other than English |
| `eval/` | The feedback judge and the extra tests (stress, robustness, transfer, revision) |

## Rules

- A prompt is found by its **file name** without `.md`, for example `grade.system`. Names are unique
  across all folders, so the code never mentions a folder.
- A file named `<step>.system.md` is the system part, and `<step>.user.md` is the user part. Some
  optional parts depend on the question type: `grade.kind.<type>`, `feedback.kind.<type>` and
  `rubric.solid.<type>`.
- Placeholders are written `{name}` and are filled in with `str.format`. So a prompt must not
  contain any other curly braces.
- English prompts never mention other languages. Anything language-specific lives in `language/`.
- `tests/test_prompts.py` checks that names are unique, that every name can be found, and that
  every prompt file is included in the experiment fingerprint.

# OCR side-track: design note

Goal: make the grader work on OCR'd handwritten answers, and measure how much marks drift.

## What is here
- `noise.py`: `noisy(text, level, seed)` and `noisy_items(items, level, seed)`. Levels light, medium, heavy. Only the student answer changes.
- `transcribe.py`: `transcribe(image_path, client)` returns text plus the words the model marked `[?word?]`.
- `prompts/ocr.transcribe.system.md`: the transcription prompt.
- `prompts/read.ocr.system.md`: extra text for the read-first pass when input came from OCR.

## Images through the CLI
The existing CLI client is text only (tools off). A probe showed `claude -p --tools Read --add-dir <folder>` lets the model open an image file by path and read it (haiku read a test image correctly, about $0.002). `transcribe` makes its own CLI call this way. The Anthropic backend sends a base64 image block instead.

## Public datasets with handwriting and teacher marks (searched, not downloaded)
Licences were not visible in search results; check each landing page before use.
- Digitized exam papers, answer keys and manual evaluations (Mendeley Data, 2026). 50 students, scans plus teacher-corrected sheets, CSV of item marks Q1-Q35 (15 short answers worth 2 marks each, 20 MCQ). Marks: yes. https://data.mendeley.com/datasets/sf3kvjwknt/1
- Handwritten ASAP short-answer scoring (Zenodo, 2020). ASAP answers rewritten by hand and scanned; scores come from ASAP. Marks: yes (original ASAP scores). https://zenodo.org/records/8088866 and github.com/catalpa-cl/handwritten-shortanswer-scoring
- Covenant University open-ended responses (MDPI Data, 2025). Handwritten, scanned, transcribed; human grader scores included. Marks: yes. https://www.mdpi.com/2306-5729/10/6/87
- Student Handwritten Exam Dataset (IEEE DataPort). 5,914 images, 21 students, CC BY 4.0. Marks: no, so only useful for transcription quality. https://ieee-dataport.org/documents/student-handwritten-exam-dataset

Best first candidate: the Mendeley set (real exam, real marks, small). The ASAP one has more answers but the handwriting is a rewrite, not exam conditions.

## Evaluation order
1. Clean typed baseline on the current datasets (already done).
2. Simulated noise at light, medium, heavy on the same items and seeds; compare marks with the clean run: mean absolute drift, bias, QWK against the teacher. Run with and without the OCR read prompt.
3. Real scans: transcribe, then grade; compare to teacher marks, and to a human-typed transcript if one exists.

Keep dev/test split by question as usual; never tune the noise rates on test.

## Integration steps (for you, not done)
1. `cli.py`: add `--ocr {light,medium,heavy}` to `run`; after loading items call `items = noisy_items(items, level, seed)`; fold the level into the run name or metrics so runs are distinguishable.
2. `config.py`: add an `ocr: str | None = None` field to the run config and include it in the cache key of anything keyed on student answers (the marking-scheme cache is by question and model answer, so it needs no change).
3. `pipeline/read.py`: when `ocr` is set, use `prompts.system("read") + "\n\n" + prompts.system("read.ocr")` in `read_answer`.
4. Optional later: `autograde transcribe <folder>` command writing items from images via `transcribe`, and a field on `Item` for low-confidence spans; feed them to the read prompt as `[?word?]` text.
5. Add the drift metrics (per-item mark difference vs the clean run) to the report; the clean run name goes in `compare`.

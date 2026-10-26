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

## Real answer sheets (done 2025-10-25)
`autograde ocr <folder> --out runs/<name> [--model haiku|sonnet|opus] [--key key.json]` reads photographed sheets (`<sheet>_p<page>.jpeg`, all pages of a sheet in one call) into `<sheet>.sheet.json` and `items.jsonl` in the `Item` format (`sheets.py`, prompt `ocr.sheet.system.md`). Questions, marks and the teacher's per-question totals are read from the page too; `model_answer` stays empty unless a key is given.

Test: 9 photos of three marked sheets (German quiz, probability quiz, network-control quiz with long derivations), scored by `python -m autograde.ocr.score data/OCR_Dataset/truth.json runs/ocr_*`. The truth file was read by Claude, not by an independent person.

| reader | German words | Probab words | Network facts | teacher totals | cost (9 pages) |
|---|---|---|---|---|---|
| Opus | 100% | 100% | 100% | all right | $0.55 |
| Sonnet | 100% | 100% | 92% | all right | $0.24 |
| Haiku | 96% | 100% | 92% | all right | $0.03 |
| RapidOCR (classical) | 64% | 57% | 0% | n/a | free, 95 s |

Findings: classical OCR cannot read this handwriting or matrices. The three Claude models agree on nearly everything; the cost of Haiku is a few misread words. Sonnet once silently "fixed" a student's wrong matrix entry before the prompt said to stay faithful, so repeat runs should be spot-checked on student mistakes. Without a rule, models split printed marks into invented smaller marks; the prompt now says one item per printed mark allocation.

Gaps: figures and tables inside questions (a joint PMF table) are not in the question text, so a reference answer drafted from the text alone is wrong for those. A student sheet has no model answer, so the key or a figure-aware solving step must come before marking. Whether a YES/NO was circled by the student is not readable.

## Classical OCR vs Claude, with tuning (2025-10-25)
Harness: `tools/ocr_bench.py` (engines, grids, scoring), `tools/ocr_prep.py` (blue-ink isolation), `tools/ocr_pipeline_eval.py` (grade the same sheets from each source). Engines need a separate venv (docling, easyocr, rapidocr-onnxruntime, transformers, opencv) and Tesseract 5.4 with `deu`/`eng` data. Truth is `data/OCR_Dataset/truth_pages.json`, read by Claude from the photos. Tuned on dev pages only (German p1, Probab p1, Network p1-2); scored on test pages (German p2, Probab p2, Network p3-4). Tiny set: 8 pages, 3 sheets, one student.

Reading accuracy, mean over pages (recall = the student's words/numbers found exactly, fuzzy = also near matches):

| reader | dev recall / fuzzy | test recall / fuzzy | seconds, 9 pages |
|---|---|---|---|
| Claude Opus | 98% / 100% | 100% / 100% | not timed, $0.90 |
| Claude Sonnet | 99% / 99% | 100% / 100% | not timed, $0.41 |
| Claude Haiku | 100% / 100% | 95% / 97% | not timed, $0.04 |
| RapidOCR tuned | 56% / 68% | 53% / 77% | 106 s |
| RapidOCR default | 54% / 65% | 56% / 72% | 105 s |
| EasyOCR (de+en) | 60% / 70% | 39% / 63% | 460 s |
| Tesseract 5.4 (deu+eng) | 42% / 48% | 37% / 58% | 109 s |
| Docling + RapidOCR | 46% / 56% | 44% / 54% | 418 s |
| TrOCR handwritten (4 short pages) | 39% / 61% on German p1, 12% / 50% on Probab p2 | | 392 s |

Key matrices and formulas (Network sheet, strict match, test pages): Claude 88-100% of listed facts; every classical engine 0-12%. On the dev pages Opus scored 50% only because it writes subscripts as a_12 where the truth string has a12; the reading itself is right (a scoring artefact, so the strict fact match undercounts it).

Tuning findings:
- RapidOCR: lower `text_score` and `det_box_thresh` (0.3), `det_unclip_ratio` 2.2, `det_limit_side_len` 1280 gave the best dev score; test fuzzy recall 72% to 77%. Small gain.
- Tesseract: the default (raw photo, `--psm 6`, `deu+eng`) won; adding German helped, preprocessing did not.
- Blue-ink isolation raises precision (Tesseract 3% to 18%) because print and teacher ink disappear, but it lowers recall, because thin strokes are lost and engines read line-oriented text. It was a net loss for EasyOCR and Tesseract.
- Docling is a layout-analysis wrapper around the same OCR engines. With RapidOCR inside it reads less than RapidOCR alone (54% vs 77% fuzzy), since regions the layout model does not call text are skipped.
- TrOCR (English line recogniser) reads digits well but drops decimal points and fails on German and on anything not a plain line.

Marking effect (20 answers: 14 Probab, 6 German; same key, same Haiku pipeline; "perfect" = the student's answers typed by hand):

| source | mean mark error vs perfect OCR | marks identical |
|---|---|---|
| Claude Sonnet | 0.075 | 90% |
| Claude Opus | 0.100 | 90% |
| Claude Haiku | 0.133 | 80% |
| RapidOCR tuned | 0.263 | 60% |
| RapidOCR default | 0.292 | 55% |
| Docling + RapidOCR | 0.445 | 50% |
| EasyOCR | 0.552 | 40% |
| TrOCR | 0.645 | 55% |
| Tesseract ink / raw | 0.762 / 0.895 | 25% / 30% |

With perfect OCR the pipeline is 0.51 marks per question away from the teacher (my own key, Haiku). Claude readers add almost nothing to that; the best classical OCR roughly doubles it, and the worst nearly quintuples it.

Not completed: Docling's own VLM (Granite-Docling) was started on the four short-answer pages and stopped after about 25 minutes without output on CPU. Docling with EasyOCR inside was only probed on one page (about 16 minutes under load, handwriting mostly missed) and not scored.

## No-GPU options (2025-10-26)
Machine: 4-core i5-8250U laptop, 7.9 GB RAM, no GPU.
- Local open VLM via llama.cpp (Qwen3-VL-2B Q4_K_M + mmproj): works only after removing `ggml-vulkan.dll` (the Vulkan backend hangs at start-up on the integrated GPU). One page took about 4 min for the vision encoder alone and was still generating after about 14 min; the output so far was the printed question text, not the handwriting. Not usable here (a batch would take days).
- Union of classical engines (their words pooled; the text-assignment step separates answers from print), 8 truth pages, near-match recall: RapidOCR alone 73%; RapidOCR + EasyOCR 89%; all five engines 94%. Marks (same 20 answers as above): RapidOCR tuned 0.263 mean error / 60% identical; union of all five 0.208 / 75% identical; Claude Haiku 0.133 / 80%. Sample is small, so treat the gap between union and Claude as indicative.

## Free hosted models (2025-10-26)
`autograde ocr <folder> --per-page --provider gemini|openrouter --model <id> --out runs/<name>` (`ocr/hosted.py`). Free only, enforced in code: Gemini models must be on the free-tier allow-list; OpenRouter ids must end in `:free` and be listed at zero price. Keys come from the git-ignored `.env`, travel in headers, and are never logged. Images sent were header-redacted copies (`tools/redact_headers.py`), since free tiers may keep the data. Scoring now tolerates LaTeX (`a_{12}`, `\lambda`), underscores and commas inside matrix rows; all engines were rescored with the same rules.

| reader (free) | dev words (exact / near) | test words | matrix and formula facts | marks: mean error / identical |
|---|---|---|---|---|
| Gemini 3.5 Flash-Lite | 100% / 100% | 100% / 100% | 100% | 0.050 / 95% |
| Gemini 3.1 Flash-Lite | 100% / 100% | 96% / 100% | 100% | 0.095 / 90% |
| Claude Sonnet (paid, for reference) | 99% / 99% | 100% / 100% | 88-100% | 0.075 / 90% |
| Claude Haiku (paid, for reference) | 100% / 100% | 95% / 97% | 100% | 0.133 / 80% |
| Pooled classical engines | 82% / 92% | 82% / 96% | 0-12% | 0.208 / 75% |

Same 20 answers as above, so a gap of 0.05 vs 0.075 is one or two answers: read it as "as good as Claude", not "better". The assignment and grading steps in this comparison still used Claude Haiku.
Not usable: Gemini 2.5 Flash and Flash-Lite ("no longer available to new users"), Gemini 3.8 Flash (timed out), OpenRouter Gemma 4 and Nemotron VL (blocked by the account's guardrail / data-policy setting, a user choice; dots-3-note returned empty).

### OpenRouter free models (2025-10-26, after the account's data-policy setting was changed)
Spend on the key stayed at $0.0000153 (unchanged) across all calls, and `hosted.py` aborts if reported cost passes $1 in a run. Results: Gemma 4 31B (`:free`) returned upstream 429 on every page for 20 minutes, so Gemma 4 26B (same pool) was not run; Nemotron 3.5 Super VL read Probab p2 perfectly with a short prompt (cost 0) but timed out upstream on the long structured prompt and was too slow in `--plain` mode to finish a 9-page run (stopped after about 20 minutes); dots-3-note returned empty replies. Verdict: free OpenRouter vision models are too slow and flaky to depend on here; use the Gemini free tier.
`--plain` (short transcription prompt, whole page as one item) and skip-failed-pages were added for such endpoints.

Paid prices on OpenRouter (per million tokens in / out): Gemini 3.1 Flash-Lite 0.25 / 1.50; Gemini 3.5 Flash-Lite 0.30 / 2.50; Claude Sonnet 5.5 2.00 / 10.00; Claude Haiku 5.5 0.10 / 0.50 (as listed). Estimated cost per page at about 2.2k input and 0.6k output tokens for Gemini (3.6k input for Claude, whose images use more tokens): 3.1 Flash-Lite about $0.0015, 3.5 Flash-Lite about $0.0022, Sonnet 5.5 about $0.013. Estimates, not measurements.

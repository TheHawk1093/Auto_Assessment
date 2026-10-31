# tools/

| Path | What it is |
|---|---|
| `sandbox/python.wasm` | Python compiled to WebAssembly. `pipeline/sandbox.py` runs student code inside it, so that the code cannot harm the computer. Only the standard library is available. It is needed only for code questions when `pipeline.code_exec` is on. See `sandbox/README.md` |

Handwriting is read through the hosted readers in `src/autograde/ocr/`, using the API keys in
`.env`. The earlier scripts for running OCR engines locally were removed from the main branch.

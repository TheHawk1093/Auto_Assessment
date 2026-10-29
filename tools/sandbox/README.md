# Sandbox interpreter

`python.wasm` is CPython 3.11.4 built for WASI, from the VMware Labs release
`python/3.11.4+20230714-11be424` of `vmware-labs/webassembly-language-runtimes`
(file `python-3.11.4.wasm`). It is git-ignored; download it again from that release if missing.

SHA-256 of the copy used so far: `422a1088378ef31788384afcdf705594d833e10c7d6336c6988e2875a269f68b`.
The release publishes no checksum file, so this value only detects later change, not a bad download.

It has only the standard library. Student code that imports numpy or pandas is not run
(`code_needs:<module>` flag) and is judged by reading.

## Check it works (run once, by hand)

```
set AUTOGRADE_REAL_SANDBOX=1
.venv\Scripts\python -m pytest tests/test_sandbox_real.py -v
```

The test runs a passing and a failing assertion, a network attempt, a file write outside the
sandbox, an endless loop and a memory hog, and expects each to be contained.

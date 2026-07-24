# Implementation Quality Checklist

> **Scope:** Software development projects only. Adapted here for a Python CLI project (not the TypeScript default).

When planning and implementing any tracked work (features, fixes, refactors), ensure the following engineering standards are met:

## 1. Boundary Checks

- [ ] Manifest JSON is validated with clear, actionable errors (missing keys, wrong types) — never a raw stack trace from `json.load`.
- [ ] External binary availability (`pandoc`, `typst`, `soffice`) is checked before use, with an install hint in the error message.

## 2. Type Safety

- [ ] Public functions have type hints (parameters + return type).
- [ ] Avoid `Any`; prefer precise types or `dataclasses`.

## 3. Failure Handling

- [ ] Subprocess calls (`pandoc`, `soffice`) use `check=True` so failures propagate as non-zero exit codes, not silently-corrupt output.
- [ ] CLI errors print to `stderr` and exit non-zero; no bare `raise` reaching the user as a traceback for expected failure modes (missing file, missing binary).

## 4. Portability

- [ ] No hardcoded paths relative to a specific host repo's structure. Manifest fields are the only source of project-specific paths.
- [ ] Bundled assets are accessed via `importlib.resources`, never `__file__`-relative string concatenation.

## 5. Code Organization

- [ ] Manifest parsing (`manifest.py`), build orchestration (`builder.py`), and post-processing (`postprocess.py`) stay separated — don't fold subprocess orchestration into parsing logic or vice versa.

## 6. Testing

- [ ] Manifest parsing has unit tests with no external binary dependency.
- [ ] Build/post-processing logic has tests that `skipif` when the relevant binary is missing (never silently pass without exercising real output when the tool is present).
- [ ] Any change to bundled templates or filters is checked against the reference consumer's manifests for output parity.

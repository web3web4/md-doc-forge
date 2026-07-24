---
created: 2026-07-24 20:30
created_by: Claude Sonnet 5 (GitHub Copilot)
edits: []
---

## Context

Initial extraction of the document-generation engine (`build-docs.sh` + helpers) out of the `saudi-realesate-tokenization-license` repo into this standalone, installable CLI. Driven by [that repo's extraction prompt](https://github.com/web3web4/saudi-realesate-tokenization-license/blob/main/execution-plans/others/prompts/2026-07-20-PROMPT_MD_DOC_FORGE_EXTRACTION.md), executed with the user's explicit authorization to implement end-to-end in this session (including git commits in this repo only).

## Plan

- [x] Scaffold repo per `web3web4/.github` engineering standards (`AGENTS.md`, `agents-instructions/`, `execution-plans/`).
- [x] Port the engine (bash + `load-manifest.py` + Lua filters + `docx-fix-tables.py` + inline PyMuPDF snippets) into a pure-Python package: `manifest.py`, `builder.py`, `postprocess.py`, `cli.py`.
- [x] Bundle default templates (`reference.docx`, `typst-header.typ`) and Lua filters as package assets, resolved via `importlib.resources`.
- [x] Add manifest-level `templates.docxReference` / `templates.typstHeader` overrides (top-level + per-document) so a second consumer with different styling doesn't need to fork the engine.
- [x] Package as pip/pipx-installable CLI (`md-doc-forge build`), entry point declared in `pyproject.toml`.
- [x] Add tests: manifest parsing (no external binary dependency) + smoke build tests that `skipif` when `pandoc`/`typst` are missing.
- [x] Add CI (`.github/workflows/ci.yml`): installs pandoc/typst/LibreOffice, runs pytest, runs an end-to-end CLI smoke build.
- [x] Verify output parity against the reference consumer's real manifest: `document.xml` inside the generated DOCX is byte-identical between the old bash pipeline and this CLI.
- [x] Verify the "arbitrary project, no source tree" scenario: installed the package (non-editable) into a fresh venv and ran `md-doc-forge build` from an unrelated directory with its own manifest.
- [x] Cut the `saudi-realesate-tokenization-license` repo over: deleted its local engine copies, updated its CI workflow and docs to install/call this CLI.

## Rationale

- **Python CLI over bash+submodule**: the deciding factor was the second real consumer beyond the reference repo — a portable agent skill that must work when dropped into an arbitrary project directory with no prepared git tree. A submodule/subtree requires exactly that preparation; an installable CLI (`pipx install git+...`) does not.
- **Rewrite engine logic in Python, not just wrap the bash script**: packaging a bash script + separate Python helper + Lua filters as pip-installable "data files with a script" is possible but awkward and platform-fragile (shebang paths, `$SCRIPT_DIR` resolution inside an installed wheel). A single Python package with `importlib.resources`-based asset loading is simpler to install, test, and reason about, and pandoc/typst/soffice are invoked identically via `subprocess` either way.
- **Template overrides included now, not deferred**: the prompt named a concrete second consumer (a `personal` repo needing non-regulatory styling) as already confirmed, not speculative — so the override mechanism was built in this pass rather than waiting for a hypothetical "Phase 3".
- **No PyPI publish yet**: only one real external consumer exists so far (the reference repo, migrated in this same session). Git-URL installs via `pipx`/`pip` are sufficient until a second consumer is actually integrated.

---

## Outcome

Implemented end-to-end and verified:

1. `pytest` — 8/8 passing (manifest parsing + smoke builds for DOCX/Typst-PDF/ODT).
2. Byte-identical `document.xml` between the legacy `saudi-realesate-tokenization-license` bash pipeline and `md-doc-forge build` run against the same real manifest.
3. Fresh non-editable install in an isolated venv, run from an unrelated directory with its own manifest — confirms no source-tree/submodule coupling.
4. `saudi-realesate-tokenization-license` repo fully cut over: local engine files deleted, CI + docs updated to install and call `md-doc-forge`.

### Notes

- LibreOffice (`soffice`) is not installed on the machine this work was done on, so the Writer-PDF pipeline (`build_writer_pdf`) was implemented per spec but not locally exercised — it will be exercised by CI (which installs LibreOffice) on first push.
- `pipx` itself is not installed locally either; verification used a plain venv + `pip install` instead, which exercises the same installed-package code path `pipx` would use (pipx is just an isolated-venv wrapper around `pip install`).
- Follow-ups (PyPI decision, `personal`-repo integration, the agent-skill wrapper) are tracked in `saudi-realesate-tokenization-license`'s `execution-plans/todo/scratch.md`, since they depend on that repo's and other repos' roadmaps, not on this engine.

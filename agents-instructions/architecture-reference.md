# Architecture & Stack Reference

> Only read this file when the task involves tech stack choices, new dependencies, or architectural decisions. Do NOT parse this every session.

## Tech Stack

- **Language**: Python 3.10+
- **Packaging**: `hatchling` build backend, `pyproject.toml`, `src/` layout
- **CLI framework**: stdlib `argparse` (no extra dependency)
- **Runtime dependencies**: `python-docx` (DOCX XML manipulation), `PyMuPDF`/`fitz` (PDF outline post-processing), `lxml` (namespace-safe XML editing)
- **External binaries** (not pip-installable, must be on `PATH`): `pandoc`, `typst`, LibreOffice (`soffice`)
- **Testing**: pytest
- **Distribution**: installable via `pipx install git+https://github.com/web3web4/md-doc-forge.git` or `pip install -e .` for local dev; no PyPI publish yet

## Standard Engineering Patterns

- **Manifest-driven, no host-repo coupling**: the engine never assumes a specific directory layout beyond what's declared in `build-manifest.json`. All manifest paths resolve relative to the manifest file's own location, not the caller's cwd — this is what makes a manifest portable across machines/CI.
- **Template overrides over forking**: consumer-specific styling (DOCX reference doc, Typst header) is supplied via manifest `templates` fields or CLI flags, never by forking the package. Bundled defaults live in `src/md_doc_forge/assets/`.
- **Bundled assets via `importlib.resources`**: never hardcode paths relative to `__file__`; use `importlib.resources.files("md_doc_forge.assets")` so assets resolve correctly whether installed as a wheel, editable install, or zipapp.
- **External binary checks fail fast with install hints**: `builder.check_dependencies()` mirrors the historical bash script's `check_dep` pattern — clear, actionable error messages, not stack traces.

## Key Architectural Decisions

- **Python CLI over bash**: the original engine was a bash script (`build-docs.sh`) calling a Python helper (`load-manifest.py`) plus inline `python3 -c` snippets. Rewritten entirely in Python so it packages as a single pip/pipx-installable unit with no bash dependency — required for the portable-skill consumer, which can't assume a POSIX shell or a writable `scripts/` directory in the host project.
- **No submodule/subtree distribution**: a git submodule/subtree requires the host repo to have a prepared git tree slot, which the agent-skill use case cannot guarantee (skills get dropped into arbitrary projects). An installable CLI (pipx) sidesteps this entirely — install once, invoke `md-doc-forge` from anywhere.
- **Lua filters and DOCX/TOC postprocessing are NOT consumer-configurable**: only visual templates (DOCX reference, Typst header) vary per consumer. The pandoc filters and postprocessing logic are engine internals that implement the page-break/TOC/table-width mechanics — these are correctness features, not styling, and stay bundled.

## Pre-commit & CI

- CI (`.github/workflows/ci.yml`) installs pandoc, Typst, and LibreOffice, then runs `pytest` and an end-to-end CLI smoke build.
- No pre-commit hooks configured yet — add `ruff`/`black` here if/when adopted.

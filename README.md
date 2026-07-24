# md-doc-forge

Manifest-driven Markdown → PDF/DOCX/ODT document generation engine, installable as a CLI. Works from any project directory — no submodules, no vendored scripts.

Extracted from the `saudi-realesate-tokenization-license` repo's document pipeline. Generates two PDF variants (Typst-rendered and LibreOffice/Writer-rendered), a styled DOCX, and an ODT from the same Markdown source, driven entirely by a `build-manifest.json` file.

## Install

```bash
pipx install "git+https://github.com/web3web4/md-doc-forge.git"
```

Or, for local development / editable installs:

```bash
pip install -e ".[dev]"
```

### Prerequisites (external binaries)

These are not pip-installable and must be present on `PATH`:

```bash
brew install pandoc
brew install typst
brew install --cask libreoffice   # macOS; use `apt install libreoffice` on Linux
```

DOCX and ODT generation need only `pandoc`. Typst PDF also needs `typst`. Writer PDF also needs LibreOffice (`soffice`).

## Usage

```bash
md-doc-forge build                                   # all formats, ./build-manifest.json
md-doc-forge build --format pdf|docx|odt|all          # restrict output format
md-doc-forge build --manifest path/to/manifest.json   # build a different manifest
md-doc-forge build --docx-reference path/to/ref.docx  # override DOCX styling for this run
md-doc-forge build --typst-header path/to/header.typ  # override Typst styling for this run
```

Relative `--manifest` paths resolve from the caller's cwd; paths **inside** a manifest resolve from the manifest file's own directory — this is what makes a manifest portable across machines and CI.

## Manifest schema

```jsonc
{
  "templates": {
    // optional; applies to all documents unless overridden per-document
    "docxReference": "path/to/reference.docx", // default: bundled template
    "typstHeader": "path/to/header.typ", // default: bundled template
  },
  "documents": [
    {
      "src": "path/to/file.md", // required; relative to the manifest file
      "outputDir": "generated/sub", // optional; default: "<src-dir>/generated"
      "outputName": "custom-name", // optional; default: src basename without .md
      "resourcePath": "path/to/res", // optional; pandoc --resource-path; default: <src-dir>
      "docxReference": "path/to/ref.docx", // optional; overrides top-level templates.docxReference
      "typstHeader": "path/to/header.typ", // optional; overrides top-level templates.typstHeader
    },
  ],
}
```

Every consumer gets sensible defaults (this project's bundled reference DOCX and Typst header) but can supply its own styling via `templates` — no fork or vendored copy required.

## Development

```bash
pip install -e ".[dev]"
pytest -v
```

See [AGENTS.md](AGENTS.md) for repo conventions and the agent workflow.

"""builder.py — Build PDF, DOCX, and ODT output from a resolved Document.

Two PDF pipelines:
  - Typst PDF  (pandoc -> typst)          -> <outputDir>/<name>.typst.pdf
  - Writer PDF (pandoc -> docx -> soffice) -> <outputDir>/<name>.pdf

Prerequisites (external binaries, not pip-installable):
  brew install pandoc                 # required for all output
  brew install typst                  # required for Typst PDF
  brew install --cask libreoffice     # required for Writer PDF (macOS)
  apt install libreoffice             # required for Writer PDF (Linux)
"""

from __future__ import annotations

import importlib.resources
import shutil
import subprocess
import sys
from pathlib import Path

from md_doc_forge.manifest import Document
from md_doc_forge.postprocess import fix_docx_tables, set_pdf_outline_view

ASSETS = importlib.resources.files("md_doc_forge.assets")

DEFAULT_DOCX_REFERENCE = str(ASSETS.joinpath("reference.docx"))
DEFAULT_TYPST_HEADER = str(ASSETS.joinpath("typst-header.typ"))
PAGE_BREAK_TOC_FILTER = str(ASSETS.joinpath("page-break-toc.lua"))
DOCX_TABLE_AUTOFIT_FILTER = str(ASSETS.joinpath("docx-table-autofit.lua"))

PANDOC_COMMON = [
    "--standalone",
    "--from=markdown+pipe_tables+backtick_code_blocks+fenced_code_blocks",
    "--shift-heading-level-by=0",
    "--columns=9999",  # prevent fixed column widths; let output engine auto-size tables
    f"--lua-filter={PAGE_BREAK_TOC_FILTER}",
]


class DependencyError(RuntimeError):
    """Raised when a required external binary/package is missing."""


def _check_binary(name: str, install_hint: str) -> None:
    if shutil.which(name) is None:
        raise DependencyError(f"'{name}' not found. Install with: {install_hint}")


def _resolve_soffice() -> str:
    if shutil.which("soffice"):
        return "soffice"
    mac_path = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    if Path(mac_path).is_file():
        return mac_path
    raise DependencyError(
        "LibreOffice not found. Install with: brew install --cask libreoffice (macOS) "
        "or apt install libreoffice (Linux)"
    )


def check_dependencies(fmt: str) -> None:
    """Verify external binaries required for the requested format are present."""
    _check_binary("pandoc", "brew install pandoc")
    if fmt in ("pdf", "all"):
        _check_binary("typst", "brew install typst")
        _resolve_soffice()


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def build_docx(doc: Document) -> Path:
    out_dir = Path(doc.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outfile = out_dir / f"{doc.output_name}.docx"
    print(f"  DOCX -> {outfile}")
    _run(
        [
            "pandoc",
            doc.src,
            *PANDOC_COMMON,
            f"--resource-path={doc.resource_path}",
            f"--reference-doc={doc.docx_reference or DEFAULT_DOCX_REFERENCE}",
            f"--lua-filter={DOCX_TABLE_AUTOFIT_FILTER}",
            "-o",
            str(outfile),
        ]
    )
    fix_docx_tables(outfile)
    return outfile


def build_typst_pdf(doc: Document) -> Path:
    out_dir = Path(doc.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outfile = out_dir / f"{doc.output_name}.typst.pdf"
    print(f"  PDF (typst)  -> {outfile}")
    _run(
        [
            "pandoc",
            doc.src,
            *PANDOC_COMMON,
            f"--resource-path={doc.resource_path}",
            f"--lua-filter={DOCX_TABLE_AUTOFIT_FILTER}",
            "--pdf-engine=typst",
            "--pdf-engine-opt=--root",
            "--pdf-engine-opt=/",
            "--pdf-engine-opt=--font-path",
            "--pdf-engine-opt=/usr/share/fonts",
            "--variable=papersize:a4",
            "--variable=mainfont:Liberation Sans",
            "--variable=margin-x:1.5cm",
            "--variable=margin-y:2cm",
            "--variable=fontsize:10.5pt",
            f"--include-in-header={doc.typst_header or DEFAULT_TYPST_HEADER}",
            "-o",
            str(outfile),
        ]
    )
    set_pdf_outline_view(outfile, use_outlines_page_mode=True)
    return outfile


def build_writer_pdf(doc: Document) -> Path:
    out_dir = Path(doc.output_dir)
    docx_file = out_dir / f"{doc.output_name}.docx"
    if not docx_file.is_file():
        build_docx(doc)
    outfile = out_dir / f"{doc.output_name}.pdf"
    print(f"  PDF (writer) -> {outfile}")
    soffice = _resolve_soffice()
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(out_dir), str(docx_file)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    set_pdf_outline_view(outfile, use_outlines_page_mode=False)
    return outfile


def build_odt(doc: Document) -> Path:
    out_dir = Path(doc.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    outfile = out_dir / f"{doc.output_name}.odt"
    print(f"  ODT  -> {outfile}")
    _run(
        [
            "pandoc",
            doc.src,
            *PANDOC_COMMON,
            f"--resource-path={doc.resource_path}",
            f"--lua-filter={DOCX_TABLE_AUTOFIT_FILTER}",
            "-o",
            str(outfile),
        ]
    )
    return outfile


def build_document(doc: Document, fmt: str) -> None:
    if not Path(doc.src).is_file():
        print(f"  SKIP: {doc.src} (not found)", file=sys.stderr)
        return

    print(f"[{doc.output_name} -> {doc.output_dir}/]")
    if fmt == "docx":
        build_docx(doc)
    elif fmt == "pdf":
        build_typst_pdf(doc)
        build_docx(doc)
        build_writer_pdf(doc)
    elif fmt == "odt":
        build_odt(doc)
    elif fmt == "all":
        build_typst_pdf(doc)
        build_docx(doc)
        build_writer_pdf(doc)
        build_odt(doc)
    else:
        raise ValueError(f"Unknown format: {fmt}. Use 'pdf', 'docx', 'odt', or 'all'.")
    print()

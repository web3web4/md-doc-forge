"""Smoke test: build a trivial document and assert output files exist.

Requires pandoc + typst on PATH; skips (rather than fails) if unavailable so
this test degrades gracefully on machines without the full toolchain (e.g.
LibreOffice is not required here — DOCX/ODT/Typst-PDF don't need it).
"""

import os
import shutil

import pytest

from md_doc_forge import builder, manifest

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")

pandoc_missing = shutil.which("pandoc") is None
typst_missing = shutil.which("typst") is None


@pytest.mark.skipif(pandoc_missing, reason="pandoc not installed")
def test_build_docx(tmp_path):
    docs = manifest.load(os.path.join(FIXTURES, "sample-manifest.json"))
    doc = docs[0]
    doc = doc.__class__(**{**doc.__dict__, "output_dir": str(tmp_path)})
    outfile = builder.build_docx(doc)
    assert outfile.is_file()
    assert outfile.stat().st_size > 0


@pytest.mark.skipif(pandoc_missing or typst_missing, reason="pandoc/typst not installed")
def test_build_typst_pdf(tmp_path):
    docs = manifest.load(os.path.join(FIXTURES, "sample-manifest.json"))
    doc = docs[0]
    doc = doc.__class__(**{**doc.__dict__, "output_dir": str(tmp_path)})
    outfile = builder.build_typst_pdf(doc)
    assert outfile.is_file()
    assert outfile.stat().st_size > 0


@pytest.mark.skipif(pandoc_missing, reason="pandoc not installed")
def test_build_odt(tmp_path):
    docs = manifest.load(os.path.join(FIXTURES, "sample-manifest.json"))
    doc = docs[0]
    doc = doc.__class__(**{**doc.__dict__, "output_dir": str(tmp_path)})
    outfile = builder.build_odt(doc)
    assert outfile.is_file()
    assert outfile.stat().st_size > 0

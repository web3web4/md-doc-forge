"""postprocess.py — Post-processing steps applied after pandoc/soffice output.

Ported verbatim (behaviorally) from the original scripts/docx-fix-tables.py
and the inline `python3 -c` PDF-outline snippets in scripts/build-docs.sh.
"""

from __future__ import annotations

from pathlib import Path

import fitz
from docx import Document as DocxDocument
from docx.oxml.ns import qn
from lxml import etree

# US Letter (8.5") with 1" margins each side = 6.5" text width = 9360 twips
PAGE_TEXT_WIDTH_TWIPS = 9360

# Heading styles pandoc uses -> TOC style mapping
HEADING_TO_TOC = {
    "Heading1": "TOC1",
    "Heading2": "TOC2",
}


def _collect_headings(body):
    """Collect heading text and bookmark IDs from the document body."""
    headings = []
    children = list(body)
    for i, elem in enumerate(children):
        if elem.tag != qn("w:p"):
            continue
        pPr = elem.find(qn("w:pPr"))
        if pPr is None:
            continue
        pStyle = pPr.find(qn("w:pStyle"))
        if pStyle is None:
            continue
        style_val = pStyle.get(qn("w:val"), "")
        if style_val not in HEADING_TO_TOC:
            continue
        text = "".join(r.text or "" for r in elem.findall(f'.//{qn("w:t")}'))
        if not text.strip():
            continue
        bookmark_name = None
        if i > 0:
            prev = children[i - 1]
            if prev.tag == qn("w:bookmarkStart"):
                bookmark_name = prev.get(qn("w:name"), "")
        headings.append(
            {
                "text": text.strip(),
                "toc_style": HEADING_TO_TOC[style_val],
                "bookmark": bookmark_name,
            }
        )
    return headings


def _make_toc_paragraph(heading):
    """Create a TOC paragraph element with the heading text."""
    p = etree.SubElement(etree.Element("dummy"), qn("w:p"))
    pPr = etree.SubElement(p, qn("w:pPr"))
    pStyle = etree.SubElement(pPr, qn("w:pStyle"))
    pStyle.set(qn("w:val"), heading["toc_style"])

    if heading["bookmark"]:
        hl = etree.SubElement(p, qn("w:hyperlink"))
        hl.set(qn("w:anchor"), heading["bookmark"])
        r = etree.SubElement(hl, qn("w:r"))
    else:
        r = etree.SubElement(p, qn("w:r"))

    t = etree.SubElement(r, qn("w:t"))
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = heading["text"]
    return p


def _populate_toc(doc):
    """Replace the empty TOC field code with actual text entries."""
    body = doc.element.body

    sdt = None
    for elem in body:
        if elem.tag == qn("w:sdt"):
            sdt_pr = elem.find(qn("w:sdtPr"))
            if sdt_pr is not None:
                dpo = sdt_pr.find(qn("w:docPartObj"))
                if dpo is not None:
                    gallery = dpo.find(qn("w:docPartGallery"))
                    if gallery is not None and "Table of Contents" in gallery.get(qn("w:val"), ""):
                        sdt = elem
                        break

    if sdt is None:
        return

    headings = _collect_headings(body)
    if not headings:
        return

    sdt_content = sdt.find(qn("w:sdtContent"))
    if sdt_content is None:
        return

    to_remove = []
    for child in sdt_content:
        if child.tag == qn("w:p"):
            pPr = child.find(qn("w:pPr"))
            if pPr is not None:
                pStyle = pPr.find(qn("w:pStyle"))
                if pStyle is not None and pStyle.get(qn("w:val")) == "TOCHeading":
                    continue
            to_remove.append(child)

    for elem in to_remove:
        sdt_content.remove(elem)

    for heading in headings:
        sdt_content.append(_make_toc_paragraph(heading))


def fix_docx_tables(path: Path | str) -> None:
    """Fix table layout (full width, breakable rows) and populate the TOC.

    Applies to a pandoc-generated DOCX file in place:
      1. Sets tblW to 100% (type=pct, w=5000)
      2. Removes tblLayout=fixed
      3. Recalculates gridCol values to fill the page text width
      4. Ensures every table row allows breaking across pages
      5. Adds keepNext to heading paragraphs directly before tables
      6. Populates the empty TOC field with actual heading text entries
    """
    path = Path(path)
    doc = DocxDocument(str(path))
    body = doc.element.body
    children = list(body)

    _populate_toc(doc)

    for i, elem in enumerate(children):
        if elem.tag != qn("w:tbl"):
            continue

        if i > 0 and children[i - 1].tag == qn("w:p"):
            para = children[i - 1]
            pPr = para.find(qn("w:pPr"))
            if pPr is not None and pPr.find(qn("w:keepNext")) is None:
                etree.SubElement(pPr, qn("w:keepNext"))

        tblPr = elem.find(qn("w:tblPr"))
        if tblPr is not None:
            tblW = tblPr.find(qn("w:tblW"))
            if tblW is not None:
                tblW.set(qn("w:w"), "5000")
                tblW.set(qn("w:type"), "pct")

            tblLayout = tblPr.find(qn("w:tblLayout"))
            if tblLayout is not None:
                tblPr.remove(tblLayout)

        tblGrid = elem.find(qn("w:tblGrid"))
        if tblGrid is not None:
            gridCols = tblGrid.findall(qn("w:gridCol"))
            n = len(gridCols)
            if n > 0:
                col_w = PAGE_TEXT_WIDTH_TWIPS // n
                remainder = PAGE_TEXT_WIDTH_TWIPS - (col_w * n)
                for j, gc in enumerate(gridCols):
                    gc.set(qn("w:w"), str(col_w + (1 if j < remainder else 0)))

        for tr in elem.findall(qn("w:tr")):
            trPr = tr.find(qn("w:trPr"))
            if trPr is None:
                trPr = etree.SubElement(tr, qn("w:trPr"))
                tr.insert(0, trPr)
            cantSplit = trPr.find(qn("w:cantSplit"))
            if cantSplit is not None:
                trPr.remove(cantSplit)

    doc.save(str(path))


def set_pdf_outline_view(path: Path | str, *, use_outlines_page_mode: bool = False) -> None:
    """Configure a PDF's bookmark/outline panel: expand top-level entries only.

    When `use_outlines_page_mode` is set, also flips the PDF's PageMode to
    `/UseOutlines` so the outline panel is shown on open (used for the Typst
    pipeline, which does not set this by default; the Writer/soffice pipeline
    already opens with a usable outline).
    """
    path = Path(path)
    doc = fitz.open(str(path))
    try:
        if use_outlines_page_mode:
            cat = doc.pdf_catalog()
            doc.xref_set_key(cat, "PageMode", "/UseOutlines")
        toc = doc.get_toc()
        if toc:
            doc.set_toc(toc, collapse=2)  # L1 expanded, L2+ collapsed
            doc.saveIncr()
    finally:
        doc.close()

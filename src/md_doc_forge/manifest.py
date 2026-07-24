"""manifest.py — Resolve a build-manifest.json into build entries.

Reads a manifest file declaring documents to build. All paths are resolved
to absolute paths relative to the manifest file's own directory (not the
caller's cwd), keeping a manifest portable: it can be built from anywhere
and moved anywhere alongside its documents.

Manifest schema (build-manifest.json):
    {
      "templates": {                    // optional, applies to all documents
        "docxReference": "path/to/reference.docx",  // optional; default: bundled template
        "typstHeader": "path/to/header.typ"         // optional; default: bundled template
      },
      "documents": [
        {
          "src": "path/to/file.md",       // required; relative to manifest
          "outputDir": "generated/sub",   // optional; default: "<src-dir>/generated"
          "outputName": "custom-name",    // optional; default: src basename without .md
          "resourcePath": "path/to/res",  // optional; default: <src-dir> (pandoc --resource-path)
          "docxReference": "path/...",    // optional; overrides top-level templates.docxReference
          "typstHeader": "path/..."       // optional; overrides top-level templates.typstHeader
        }
      ]
    }
"""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    src: str
    resource_path: str
    output_dir: str
    output_name: str
    docx_reference: str | None
    typst_header: str | None


def _resolve_path(manifest_dir: str, value: str | None) -> str | None:
    if value is None:
        return None
    return os.path.normpath(os.path.join(manifest_dir, value))


def load(manifest_path: str) -> list[Document]:
    """Parse a manifest file and return the resolved list of documents.

    Exits the process with a clear error message on any structural problem,
    matching the historical behavior of the bash/load-manifest.py pipeline.
    """
    if not os.path.isfile(manifest_path):
        sys.exit(f"ERROR: manifest not found: {manifest_path}")

    with open(manifest_path) as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            sys.exit(f"ERROR: invalid JSON in {manifest_path}: {e}")

    documents = data.get("documents")
    if not isinstance(documents, list) or not documents:
        sys.exit(f'ERROR: {manifest_path} must contain a non-empty "documents" array')

    manifest_dir = os.path.dirname(os.path.abspath(manifest_path))

    top_templates = data.get("templates", {})
    if not isinstance(top_templates, dict):
        sys.exit(f'ERROR: "templates" in {manifest_path} must be an object')
    top_docx_ref = _resolve_path(manifest_dir, top_templates.get("docxReference"))
    top_typst_header = _resolve_path(manifest_dir, top_templates.get("typstHeader"))

    result: list[Document] = []
    for i, doc in enumerate(documents):
        src_rel = doc.get("src")
        if not src_rel:
            sys.exit(f'ERROR: documents[{i}] in {manifest_path} is missing required "src"')
        src_dir = os.path.dirname(src_rel)

        src = os.path.normpath(os.path.join(manifest_dir, src_rel))
        out_dir = os.path.normpath(
            os.path.join(manifest_dir, doc.get("outputDir", os.path.join(src_dir, "generated")))
        )
        resource_path = os.path.normpath(
            os.path.join(manifest_dir, doc.get("resourcePath", src_dir))
        )
        out_name = doc.get("outputName", os.path.splitext(os.path.basename(src_rel))[0])

        docx_reference = _resolve_path(manifest_dir, doc.get("docxReference")) or top_docx_ref
        typst_header = _resolve_path(manifest_dir, doc.get("typstHeader")) or top_typst_header

        result.append(
            Document(
                src=src,
                resource_path=resource_path,
                output_dir=out_dir,
                output_name=out_name,
                docx_reference=docx_reference,
                typst_header=typst_header,
            )
        )
    return result

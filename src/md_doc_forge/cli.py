"""cli.py — `md-doc-forge` command-line entry point.

Usage:
    md-doc-forge build                                   # All formats, ./build-manifest.json
    md-doc-forge build --format pdf|docx|odt|all          # Restrict output format
    md-doc-forge build --manifest path/to/manifest.json   # Build a different manifest
    md-doc-forge build --docx-reference path/to/ref.docx  # Override DOCX template for this run
    md-doc-forge build --typst-header path/to/header.typ  # Override Typst header for this run

Relative --manifest paths resolve from the caller's cwd; paths inside a
manifest resolve from the manifest file's own directory.
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import sys

from md_doc_forge import manifest as manifest_module
from md_doc_forge.builder import DependencyError, build_document, check_dependencies


def _build(args: argparse.Namespace) -> int:
    manifest_path = args.manifest
    if not os.path.isfile(manifest_path):
        print(f"ERROR: manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    docs = manifest_module.load(manifest_path)

    if args.docx_reference:
        docx_reference = os.path.abspath(args.docx_reference)
        docs = [dataclasses.replace(d, docx_reference=docx_reference) for d in docs]
    if args.typst_header:
        typst_header = os.path.abspath(args.typst_header)
        docs = [dataclasses.replace(d, typst_header=typst_header) for d in docs]

    try:
        check_dependencies(args.format)
    except DependencyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    print("Building documents...\n")
    for doc in docs:
        build_document(doc, args.format)

    print("Done. Output:\n")
    for out_dir in sorted({d.output_dir for d in docs}):
        print(f"{out_dir}/:")
        if os.path.isdir(out_dir):
            for name in sorted(os.listdir(out_dir)):
                print(f"  {name}")
        print()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="md-doc-forge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_cmd = subparsers.add_parser("build", help="Build documents declared in a manifest")
    build_cmd.add_argument(
        "--manifest",
        default="build-manifest.json",
        help="Path to build-manifest.json (default: ./build-manifest.json)",
    )
    build_cmd.add_argument(
        "--format",
        choices=["pdf", "docx", "odt", "all"],
        default="all",
        help="Restrict output format (default: all)",
    )
    build_cmd.add_argument(
        "--docx-reference",
        help="Override the DOCX reference template for this run (all documents)",
    )
    build_cmd.add_argument(
        "--typst-header",
        help="Override the Typst header template for this run (all documents)",
    )
    build_cmd.set_defaults(func=_build)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()

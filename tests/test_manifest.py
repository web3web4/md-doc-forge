import json
import os

from md_doc_forge import manifest


FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def test_load_resolves_defaults():
    docs = manifest.load(os.path.join(FIXTURES, "sample-manifest.json"))
    assert len(docs) == 1
    doc = docs[0]
    assert doc.src == os.path.join(FIXTURES, "sample.md")
    assert doc.output_dir == os.path.join(FIXTURES, "generated")
    assert doc.output_name == "sample"
    assert doc.docx_reference is None
    assert doc.typst_header is None


def test_load_missing_manifest_exits(tmp_path):
    import pytest

    with pytest.raises(SystemExit):
        manifest.load(str(tmp_path / "does-not-exist.json"))


def test_load_missing_documents_key_exits(tmp_path):
    import pytest

    bad = tmp_path / "bad-manifest.json"
    bad.write_text(json.dumps({}))
    with pytest.raises(SystemExit):
        manifest.load(str(bad))


def test_load_template_overrides(tmp_path):
    (tmp_path / "doc.md").write_text("# Hi\n")
    (tmp_path / "custom-ref.docx").write_bytes(b"")
    (tmp_path / "custom-header.typ").write_text("")
    manifest_data = {
        "templates": {"docxReference": "custom-ref.docx", "typstHeader": "custom-header.typ"},
        "documents": [{"src": "doc.md"}],
    }
    manifest_path = tmp_path / "build-manifest.json"
    manifest_path.write_text(json.dumps(manifest_data))

    docs = manifest.load(str(manifest_path))
    assert docs[0].docx_reference == str(tmp_path / "custom-ref.docx")
    assert docs[0].typst_header == str(tmp_path / "custom-header.typ")


def test_per_document_override_wins_over_top_level(tmp_path):
    (tmp_path / "doc.md").write_text("# Hi\n")
    (tmp_path / "top-ref.docx").write_bytes(b"")
    (tmp_path / "doc-ref.docx").write_bytes(b"")
    manifest_data = {
        "templates": {"docxReference": "top-ref.docx"},
        "documents": [{"src": "doc.md", "docxReference": "doc-ref.docx"}],
    }
    manifest_path = tmp_path / "build-manifest.json"
    manifest_path.write_text(json.dumps(manifest_data))

    docs = manifest.load(str(manifest_path))
    assert docs[0].docx_reference == str(tmp_path / "doc-ref.docx")

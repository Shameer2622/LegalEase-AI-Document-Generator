from backend.services.document_formatter import (
    export_document,
    format_html_preview,
    sanitize_text,
)


def test_sanitize_text():
    value = "Hello\u2014world\u2019s"
    assert sanitize_text(value) == "Hello-world's"


def test_html_preview():
    html = format_html_preview("TITLE\n\nFirst paragraph.")
    assert "TITLE" in html
    assert "First paragraph." in html


def test_txt_export():
    data, media_type, extension = export_document(
        "txt",
        "Sample legal text.",
        "Agreement",
    )
    assert data == b"Sample legal text."
    assert "text/plain" in media_type
    assert extension == ".txt"


def test_docx_export():
    data, media_type, extension = export_document(
        "docx",
        "AGREEMENT\n\nThis is a draft.",
        "Agreement",
    )
    assert data[:2] == b"PK"
    assert "wordprocessingml.document" in media_type
    assert extension == ".docx"


def test_pdf_export():
    data, media_type, extension = export_document(
        "pdf",
        "AGREEMENT\n\nThis is a draft.",
        "Agreement",
    )
    assert data.startswith(b"%PDF")
    assert media_type == "application/pdf"
    assert extension == ".pdf"

"""Unit tests for document extractor (domain layer). No server or external systems."""

import pytest

from src.domain.extractor import SimpleDocumentExtractor


def test_plain_text_extraction() -> None:
    extractor = SimpleDocumentExtractor(["text/plain"])
    content = "hello world".encode("utf-8")
    result = extractor.extract(content, "text/plain")
    if result != "hello world":
        raise AssertionError(f"Expected 'hello world', got {result!r}")


def test_pdf_extraction_uses_pdf_handler(monkeypatch: pytest.MonkeyPatch) -> None:
    extractor = SimpleDocumentExtractor(["application/pdf"])

    def fake_extract_pdf(content: bytes) -> str:
        return "pdf text"

    monkeypatch.setattr(
        extractor,
        "_extract_pdf",
        fake_extract_pdf,
    )

    result = extractor.extract(b"%PDF-1.4", "application/pdf")
    if result != "pdf text":
        raise AssertionError(f"Expected 'pdf text', got {result!r}")


def test_extract_unsupported_type_raises() -> None:
    extractor = SimpleDocumentExtractor(["text/plain"])
    try:
        extractor.extract(b"hello", "application/pdf")
        raise AssertionError("Expected ValueError for unsupported content type")
    except ValueError as exc:
        message = str(exc)
        if "Unsupported content type" not in message:
            raise AssertionError(f"Unexpected error message: {message!r}")


def test_extract_with_allowed_but_unhandled_type_raises() -> None:
    """If content type is allowed but not plain/pdf, extractor should still raise."""
    extractor = SimpleDocumentExtractor(["application/octet-stream"])
    try:
        extractor.extract(b"data", "application/octet-stream")
        raise AssertionError("Expected ValueError for unhandled but allowed content type")
    except ValueError as exc:
        message = str(exc)
        if "Unsupported content type" not in message:
            raise AssertionError(f"Unexpected error message: {message!r}")


def test_extract_empty_content_returns_empty() -> None:
    extractor = SimpleDocumentExtractor(["text/plain"])
    result = extractor.extract(b"", "text/plain")
    if result != "":
        raise AssertionError(f"Expected empty string for empty content, got {result!r}")


def test_extract_pdf_reads_pages(monkeypatch: pytest.MonkeyPatch) -> None:
    """Exercise SimpleDocumentExtractor._extract_pdf happy path."""

    class FakePage:
        def __init__(self, text: str) -> None:
            self._text = text

        def extract_text(self) -> str:
            return self._text

    class FakePdf:
        def __init__(self) -> None:
            self.pages = [FakePage("page1"), FakePage("page2")]

        def __enter__(self) -> "FakePdf":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
            return None

    import src.domain.extractor as extractor_module  # local import for monkeypatch

    monkeypatch.setattr(extractor_module.pdfplumber, "open", lambda _: FakePdf())

    extractor = SimpleDocumentExtractor(["application/pdf"])
    result = extractor.extract(b"%PDF-1.4", "application/pdf")
    if result != "page1\npage2":
        raise AssertionError(f"Expected joined page text, got {result!r}")

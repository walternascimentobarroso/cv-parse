"""Unit tests for document extractor (domain layer). No server or external systems."""

from src.domain.extractor import SimpleDocumentExtractor


def test_plain_text_extraction() -> None:
    extractor = SimpleDocumentExtractor(["text/plain"])
    content = "hello world".encode("utf-8")
    result = extractor.extract(content, "text/plain")
    if result != "hello world":
        raise AssertionError(f"Expected 'hello world', got {result!r}")


def test_pdf_extraction_uses_pdf_handler(monkeypatch: object) -> None:
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

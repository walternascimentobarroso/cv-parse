"""Unit tests for extractor registry and extractor strategies."""

from __future__ import annotations

import pytest

from src.infra.extractors.base import DocumentExtractorStrategy
from src.infra.extractors.pdf import PdfExtractor
from src.infra.extractors.plain_text import PlainTextExtractor
from src.infra.extractors.registry import ExtractorRegistry


def test_registry_plain_text() -> None:
    registry = ExtractorRegistry(mime_type_plain="text/plain", mime_type_pdf="application/pdf")
    result = registry.extract(b"hello world", "text/plain")
    if result != "hello world":
        raise AssertionError(f"Expected 'hello world', got {result!r}")


def test_registry_unsupported_type_raises() -> None:
    registry = ExtractorRegistry(mime_type_plain="text/plain", mime_type_pdf="application/pdf")
    try:
        registry.extract(b"x", "image/jpeg")
        raise AssertionError("Expected ValueError for unsupported type")
    except ValueError as e:
        if "Unsupported" not in str(e):
            raise AssertionError(f"Expected 'Unsupported' in error: {e}") from e


def test_registry_pdf_invalid_raises_value_error() -> None:
    """Registry delegates to PDF strategy; invalid PDF raises ValueError (logged by strategy)."""
    registry = ExtractorRegistry(mime_type_plain="text/plain", mime_type_pdf="application/pdf")
    try:
        registry.extract(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n", "application/pdf")
        raise AssertionError("Expected ValueError for invalid PDF")
    except ValueError as exc:
        if "PDF extraction failed" not in str(exc):
            raise AssertionError(f"Expected 'PDF extraction failed' in error: {exc}") from exc


def test_plain_text_extractor_empty_and_non_empty() -> None:
    extractor: DocumentExtractorStrategy = PlainTextExtractor()
    empty_result = extractor.extract(b"")
    if empty_result != "":
        raise AssertionError(f"Expected empty string for empty content, got {empty_result!r}")
    result = extractor.extract(b"hello")
    if result != "hello":
        raise AssertionError(f"Expected 'hello', got {result!r}")


def test_pdf_extractor_happy_path_and_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    extractor = PdfExtractor()

    class FakePage:
        def __init__(self, text: str) -> None:
            self._text = text

        def extract_text(self) -> str:
            return self._text

    class FakePdf:
        def __init__(self) -> None:
            self.pages = [FakePage("p1"), FakePage("p2")]

        def __enter__(self) -> "FakePdf":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
            return None

    import src.infra.extractors.pdf as pdf_module

    monkeypatch.setattr(pdf_module.pdfplumber, "open", lambda _: FakePdf())

    empty_result = extractor.extract(b"")
    if empty_result != "":
        raise AssertionError(f"Expected empty string for empty content, got {empty_result!r}")

    result = extractor.extract(b"%PDF-1.4")
    if result != "p1\np2":
        raise AssertionError(f"Expected joined page text, got {result!r}")


def test_pdf_extractor_logs_and_raises_on_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    extractor = PdfExtractor()

    import src.infra.extractors.pdf as pdf_module

    def boom(_buffer):
        raise RuntimeError("pdf boom")

    monkeypatch.setattr(pdf_module.pdfplumber, "open", boom)

    try:
        extractor.extract(b"%PDF-1.4")
        raise AssertionError("Expected ValueError from PdfExtractor on failure")
    except ValueError as exc:
        if "PDF extraction failed" not in str(exc):
            raise AssertionError(f"Unexpected error message: {exc!r}") from exc

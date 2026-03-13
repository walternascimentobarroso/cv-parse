"""Unit tests for extractor registry (strategy selection)."""

from __future__ import annotations

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
    except ValueError as e:
        if "PDF extraction failed" not in str(e):
            raise AssertionError(f"Expected 'PDF extraction failed' in error: {e}") from e

"""Unit tests for Settings and content-type parsing."""

from __future__ import annotations

import pytest

from src.infra.config import Settings, _default_content_types_list, _parse_allowed_content_types


def test_default_content_types_list() -> None:
    values = _default_content_types_list()
    if "application/pdf" not in values or "text/plain" not in values:
        msg = f"Expected default types to include pdf and text, got {values!r}"
        raise AssertionError(msg)


def test_parse_allowed_content_types_empty_uses_default() -> None:
    result = _parse_allowed_content_types("")
    default_values = _default_content_types_list()
    if result != default_values:
        msg = f"Expected default content types, got {result!r}"
        raise AssertionError(msg)


def test_parse_allowed_content_types_json_list() -> None:
    value = '["application/pdf", "text/plain"]'
    result = _parse_allowed_content_types(value)
    if result != ["application/pdf", "text/plain"]:
        msg = f"Unexpected parsed list from JSON: {result!r}"
        raise AssertionError(msg)


def test_parse_allowed_content_types_csv_and_trims() -> None:
    value = " application/pdf , text/plain , "
    result = _parse_allowed_content_types(value)
    if result != ["application/pdf", "text/plain"]:
        msg = f"Unexpected parsed list from CSV: {result!r}"
        raise AssertionError(msg)


def test_settings_allowed_content_types_property_uses_parser() -> None:
    settings = Settings()
    values = settings.allowed_content_types
    if "application/pdf" not in values or "text/plain" not in values:
        msg = f"Expected defaults to include pdf and text, got {values!r}"
        raise AssertionError(msg)


def test_parse_allowed_content_types_json_non_list_uses_default() -> None:
    value = '{"not": "a list"}'
    result = _parse_allowed_content_types(value)
    default_values = _default_content_types_list()
    if result != default_values:
        msg = f"Expected default content types for non-list JSON, got {result!r}"
        raise AssertionError(msg)


def test_settings_mongodb_validator_rejects_blank() -> None:
    """Covers _require_non_empty when URI/DB missing (Pyright-friendly defaults)."""
    with pytest.raises(ValueError, match="MongoDB settings must be provided"):
        Settings._require_non_empty("")
    with pytest.raises(ValueError, match="MongoDB settings must be provided"):
        Settings._require_non_empty("   ")

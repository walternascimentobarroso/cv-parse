from __future__ import annotations

from src.infra.cv_extractors.certification_structured import (
    certification_details_from_strings,
)


def test_certification_details_ignores_blank_and_parses_separator() -> None:
    certs = ["  ", "Python Course — Coursera"]
    result = certification_details_from_strings(certs)
    expected = [{"name": "Python Course", "issuer": "Coursera"}]
    if result != expected:
        raise AssertionError(f"Expected {expected!r}, got {result!r}")

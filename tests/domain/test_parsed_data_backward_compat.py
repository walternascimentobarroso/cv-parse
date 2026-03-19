"""Legacy parsed_data keys and types remain after 008 enhancements."""

from __future__ import annotations

from pathlib import Path

from src.domain.cv_parser import parse_cv

_FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "sample_cv_text.txt"


def test_backward_compat_keys_and_types() -> None:
    text = _FIXTURE.read_text(encoding="utf-8")
    result = parse_cv(text)

    for key in ("experience", "education", "skills", "certifications", "personal_info"):
        if not hasattr(result, key):
            raise AssertionError(f"Missing attribute {key!r}")

    if not isinstance(result.experience, list):
        raise AssertionError("experience must be list")
    if not isinstance(result.skills, list):
        raise AssertionError("skills must be list of strings")
    if not isinstance(result.certifications, list):
        raise AssertionError("certifications must be list")

    for entry in result.experience:
        for k in ("company", "role", "start_date", "end_date", "description"):
            if k not in entry:
                raise AssertionError(f"experience entry missing {k!r}")

    pi = result.personal_info
    for k in ("full_name", "email", "phone", "linkedin", "github", "summary"):
        if k not in pi:
            raise AssertionError(f"personal_info missing {k!r}")

    if result.personal_info.get("email") != "alice@smith.dev":
        raise AssertionError("Expected fixture email preserved")

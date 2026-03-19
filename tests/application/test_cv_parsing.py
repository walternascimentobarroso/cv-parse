from __future__ import annotations

import os
from typing import Any

from src.application import cv_parsing
from src.application.cv_parsing import _merge_flat_skills, build_parsed_cv, empty_parsed_cv


def test_empty_parsed_cv_has_expected_shape() -> None:
    data = empty_parsed_cv()
    if data.experience != []:
        msg = f"Expected empty experience, got {data.experience!r}"
        raise AssertionError(msg)
    if data.education != []:
        msg = f"Expected empty education, got {data.education!r}"
        raise AssertionError(msg)
    if data.skills != []:
        msg = f"Expected empty skills, got {data.skills!r}"
        raise AssertionError(msg)
    if data.certifications != []:
        msg = f"Expected empty certifications, got {data.certifications!r}"
        raise AssertionError(msg)
    if not isinstance(data.personal_info, dict):
        msg = f"Expected personal_info dict, got {type(data.personal_info)!r}"
        raise AssertionError(msg)
    if "email" not in data.personal_info:
        msg = f"Expected 'email' in personal_info, got {list(data.personal_info)!r}"
        raise AssertionError(msg)


def test_merge_flat_skills_ignores_empty_tokens() -> None:
    catalog = ["Python"]
    # Second hard skill is just whitespace and should be ignored.
    hard = ["Go", "   "]
    soft: list[str] = []
    result = _merge_flat_skills(catalog, hard, soft)
    if "Python" not in result or "Go" not in result:
        msg = f"Expected Python and Go in result, got {result!r}"
        raise AssertionError(msg)
    if not all(x.strip() for x in result):
        msg = f"Expected no empty tokens in result, got {result!r}"
        raise AssertionError(msg)


def test_build_parsed_cv_uses_basic_experience_when_disabled(monkeypatch) -> None:
    captured: dict[str, Any] = {}

    def fake_split_into_sections(_raw: str) -> dict[str, str]:
        return {"experience": "Role at Co\n2020 - 2022"}

    def fake_parse_experience_section(section: str) -> list[dict[str, object]]:
        captured["called_with"] = section
        return [{"company": "Co", "role": "Role"}]

    def fail_parse_experience_multi(_section: str) -> list[dict[str, object]]:
        msg = "parse_experience_multi should not be called when disabled"
        raise AssertionError(msg)

    monkeypatch.setenv("CV_PARSER_ENHANCED", "0")

    monkeypatch.setattr(cv_parsing, "split_into_sections", fake_split_into_sections)
    monkeypatch.setattr(
        cv_parsing,
        "parse_experience_section",
        fake_parse_experience_section,
    )
    monkeypatch.setattr(cv_parsing, "parse_experience_multi", fail_parse_experience_multi)

    data = build_parsed_cv("dummy text")
    if captured["called_with"] != "Role at Co\n2020 - 2022":
        msg = f"Expected section, got {captured['called_with']!r}"
        raise AssertionError(msg)
    if data.experience != [{"company": "Co", "role": "Role"}]:
        msg = f"Expected experience, got {data.experience!r}"
        raise AssertionError(msg)

    # Clean up env override for other tests
    os.environ.pop("CV_PARSER_ENHANCED", None)

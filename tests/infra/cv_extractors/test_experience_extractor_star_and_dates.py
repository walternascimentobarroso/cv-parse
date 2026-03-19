from __future__ import annotations

from src.infra.cv_extractors.experience_extractor import (
    _line_has_compact_date_range,
    _merge_star_description,
    _star_rest,
)


def test_merge_star_description_appends_other_block() -> None:
    description = (
        "Situation: context here\nTask: do something important\n"
        "Action: implemented feature\nResult: improved performance\n"
        "Additional note not tagged"
    )
    body, responsibilities, achievements = _merge_star_description(description)
    if "Additional note not tagged" not in body:
        msg = f"Expected 'Additional note not tagged' in body, got {body!r}"
        raise AssertionError(msg)
    if not any("Task" not in x for x in responsibilities):
        msg = f"Expected mixed responsibilities, got {responsibilities!r}"
        raise AssertionError(msg)
    if "improved performance" not in "\n".join(achievements):
        msg = f"Expected in achievements, got {achievements!r}"
        raise AssertionError(msg)


def test_merge_star_description_no_other_or_duplicate_other_list() -> None:
    description = (
        "Situation: context here\nTask: do something important\n"
        "Action: implemented feature\nResult: improved performance"
    )
    body, responsibilities, achievements = _merge_star_description(description)
    if "Additional note" in body:
        msg = f"Expected no 'Additional note' in body, got {body!r}"
        raise AssertionError(msg)
    if not responsibilities:
        msg = f"Expected non-empty responsibilities, got {responsibilities!r}"
        raise AssertionError(msg)
    if not achievements:
        msg = f"Expected non-empty achievements, got {achievements!r}"
        raise AssertionError(msg)


def test_merge_star_description_empty_description_returns_defaults() -> None:
    body, responsibilities, achievements = _merge_star_description("")
    if body != "":
        msg = f"Expected empty body, got {body!r}"
        raise AssertionError(msg)
    if responsibilities != []:
        msg = f"Expected empty responsibilities, got {responsibilities!r}"
        raise AssertionError(msg)
    if achievements != []:
        msg = f"Expected empty achievements, got {achievements!r}"
        raise AssertionError(msg)


def test_merge_star_description_without_star_returns_original() -> None:
    description = "Plain line 1\nPlain line 2"
    body, responsibilities, achievements = _merge_star_description(description)
    if body != description:
        msg = f"Expected body equal to description, got {body!r}"
        raise AssertionError(msg)
    if responsibilities != []:
        msg = f"Expected empty responsibilities, got {responsibilities!r}"
        raise AssertionError(msg)
    if achievements != []:
        msg = f"Expected empty achievements, got {achievements!r}"
        raise AssertionError(msg)


def test_star_rest_returns_original_when_no_pattern_matches() -> None:
    line = "Plain line without STAR label"
    out = _star_rest(line)
    if out != line:
        msg = f"Expected out == line, got {out!r}"
        raise AssertionError(msg)


def test_line_has_compact_date_range_true_and_false_paths() -> None:
    if not _line_has_compact_date_range("Jan 2020 - Feb 2021"):
        msg = "Expected True for month-year range"
        raise AssertionError(msg)
    if not _line_has_compact_date_range("2020 - Present"):
        msg = "Expected True for year-Present"
        raise AssertionError(msg)
    long_line = "x" * 81
    if _line_has_compact_date_range(long_line):
        msg = "Expected False for line longer than 80 chars"
        raise AssertionError(msg)

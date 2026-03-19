from __future__ import annotations

from src.infra.cv_extractors.experience_extractor import (
    _line_has_compact_date_range,
    _merge_star_description,
    _star_rest,
)


def test_merge_star_description_appends_other_block() -> None:
    description = "\n".join(
        [
            "Situation: context here",
            "Task: do something important",
            "Action: implemented feature",
            "Result: improved performance",
            "Additional note not tagged",
        ]
    )
    body, responsibilities, achievements = _merge_star_description(description)
    if "Additional note not tagged" not in body:
        raise AssertionError(f"Expected 'Additional note not tagged' in body, got {body!r}")
    if not any("Task" not in x for x in responsibilities):
        raise AssertionError(f"Expected mixed responsibilities, got {responsibilities!r}")
    if "improved performance" not in "\n".join(achievements):
        raise AssertionError(f"Expected in achievements, got {achievements!r}")


def test_merge_star_description_no_other_or_duplicate_other_list() -> None:
    description = "\n".join(
        [
            "Situation: context here",
            "Task: do something important",
            "Action: implemented feature",
            "Result: improved performance",
        ]
    )
    body, responsibilities, achievements = _merge_star_description(description)
    if "Additional note" in body:
        raise AssertionError(f"Expected no 'Additional note' in body, got {body!r}")
    if not responsibilities:
        raise AssertionError(f"Expected non-empty responsibilities, got {responsibilities!r}")
    if not achievements:
        raise AssertionError(f"Expected non-empty achievements, got {achievements!r}")


def test_merge_star_description_empty_description_returns_defaults() -> None:
    body, responsibilities, achievements = _merge_star_description("")
    if body != "":
        raise AssertionError(f"Expected empty body, got {body!r}")
    if responsibilities != []:
        raise AssertionError(f"Expected empty responsibilities, got {responsibilities!r}")
    if achievements != []:
        raise AssertionError(f"Expected empty achievements, got {achievements!r}")


def test_merge_star_description_without_star_returns_original() -> None:
    description = "Plain line 1\nPlain line 2"
    body, responsibilities, achievements = _merge_star_description(description)
    if body != description:
        raise AssertionError(f"Expected body equal to description, got {body!r}")
    if responsibilities != []:
        raise AssertionError(f"Expected empty responsibilities, got {responsibilities!r}")
    if achievements != []:
        raise AssertionError(f"Expected empty achievements, got {achievements!r}")


def test_star_rest_returns_original_when_no_pattern_matches() -> None:
    line = "Plain line without STAR label"
    out = _star_rest(line)
    if out != line:
        raise AssertionError(f"Expected out == line, got {out!r}")


def test_line_has_compact_date_range_true_and_false_paths() -> None:
    if not _line_has_compact_date_range("Jan 2020 - Feb 2021"):
        raise AssertionError("Expected True for month-year range")
    if not _line_has_compact_date_range("2020 - Present"):
        raise AssertionError("Expected True for year-Present")
    long_line = "x" * 81
    if _line_has_compact_date_range(long_line):
        raise AssertionError("Expected False for line longer than 80 chars")

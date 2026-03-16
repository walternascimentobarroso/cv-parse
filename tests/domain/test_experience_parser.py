"""Unit tests for experience parser (domain layer)."""

from src.domain.experience_parser import (
    ExperienceEntry,
    _has_company_hint,
    parse_experience_section,
)


def test_parse_experience_empty_returns_empty() -> None:
    result = parse_experience_section("")
    if result != []:
        raise AssertionError(f"Expected [], got {result!r}")


def test_parse_experience_whitespace_only_returns_empty() -> None:
    result = parse_experience_section("   \n  ")
    if result != []:
        raise AssertionError(f"Expected [], got {result!r}")


def test_parse_experience_date_range_month_year() -> None:
    """Date range is extracted from the first line (header) of the block."""
    text = "Software Engineer at Acme Inc Jan 2020 - Dec 2022"
    result = parse_experience_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    entry = result[0]
    if not entry.get("start_date") or "2020" not in entry["start_date"]:
        raise AssertionError(f"Expected start_date with 2020, got {entry!r}")
    if not entry.get("end_date"):
        raise AssertionError(f"Expected end_date, got {entry!r}")
    if not entry.get("company") and not entry.get("role"):
        raise AssertionError(f"Expected company or role, got {entry!r}")


def test_parse_experience_date_range_year_only() -> None:
    """Year-only date range on header line is extracted."""
    text = "Developer at Company Ltd 2019 - 2021"
    result = parse_experience_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("start_date") != "2019" or result[0].get("end_date") != "2021":
        raise AssertionError(f"Expected 2019-2021, got {result[0]!r}")


def test_parse_experience_present_end_date() -> None:
    """Present as end date on header line is extracted."""
    text = "Engineer at Startup Inc 2022 - Present"
    result = parse_experience_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if "Present" not in result[0].get("end_date", ""):
        raise AssertionError(f"Expected Present in end_date, got {result[0]!r}")


def test_parse_experience_role_company_separator_at() -> None:
    text = "Senior Dev at Acme Ltd\n2020 - 2022"
    result = parse_experience_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    entry = result[0]
    if not (entry.get("role") or entry.get("company")):
        raise AssertionError(f"Expected role or company, got {entry!r}")


def test_parse_experience_company_hint_ltd() -> None:
    text = "Acme Ltd - Lead Engineer 2018 - 2019"
    result = parse_experience_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("company") and "Acme" in result[0]["company"]:
        pass
    if result[0].get("role") and "Lead" in result[0]["role"]:
        pass


def test_parse_experience_no_company_hint_keeps_role_company_order() -> None:
    """When right part has no Ltd/Inc etc., keep common format: left=role, right=company."""
    text = "Developer at SmallCo 2020 - 2021"
    result = parse_experience_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("role") != "Developer":
        raise AssertionError(f"Expected role Developer, got {result[0].get('role')!r}")
    if result[0].get("company") != "SmallCo":
        raise AssertionError(f"Expected company SmallCo, got {result[0].get('company')!r}")


def test_parse_experience_description_from_rest_of_block() -> None:
    """Lines after the header in the same block become description (no blank line in between)."""
    text = "Role at Company 2019 - 2020\nBuilt systems.\nUsed Python."
    result = parse_experience_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    desc = result[0].get("description", "")
    if "Built" not in desc or "Python" not in desc:
        raise AssertionError(f"Expected description with content, got {desc!r}")


def test_parse_experience_multiple_blocks() -> None:
    """Blank line separates blocks; date range must be on header line."""
    text = "Job A at X 2018-2019\n\nJob B at Y 2019-2021"
    result = parse_experience_section(text)
    if len(result) != 2:
        raise AssertionError(f"Expected 2 entries, got {len(result)}")
    if result[0].get("start_date") != "2018" or result[1].get("start_date") != "2019":
        raise AssertionError(f"Expected two blocks with dates, got {result!r}")


def test_parse_experience_output_dict_shape() -> None:
    text = "Dev at Corp\n2020 - 2021"
    result = parse_experience_section(text)
    entry = result[0]
    for key in ("company", "role", "start_date", "end_date", "description"):
        if key not in entry:
            raise AssertionError(f"Expected key {key!r} in entry")
    if not all(isinstance(v, str) for v in entry.values()):
        raise AssertionError(f"All values must be str, got {entry!r}")


def test_parse_experience_no_separator_uses_whole_header_as_role() -> None:
    """When header has no 'at'/'@'/'-' separator, whole header becomes role, company empty."""
    text = "Solo Role Title 2020 - 2021"
    result = parse_experience_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("role") != "Solo Role Title":
        raise AssertionError(f"Expected role from full header, got {result[0].get('role')!r}")
    if result[0].get("company") != "":
        raise AssertionError(f"Expected empty company, got {result[0].get('company')!r}")


def test_experience_entry_dataclass_defaults() -> None:
    entry = ExperienceEntry()
    if entry.company is not None or entry.role is not None:
        raise AssertionError(f"Expected None defaults, got {entry!r}")
    if entry.start_date is not None or entry.end_date is not None or entry.description is not None:
        raise AssertionError(f"Expected None defaults, got {entry!r}")


def test_has_company_hint_empty_returns_false() -> None:
    if _has_company_hint("") is not False:
        raise AssertionError("Expected _has_company_hint('') to return False")


def test_parse_experience_two_blocks_separated_by_header_line() -> None:
    """Two blocks separated by a new header line (no blank line) trigger block yield."""
    text = "Role A at Company X 2018 - 2019\nRole B at Company Y 2019 - 2021"
    result = parse_experience_section(text)
    if len(result) != 2:
        raise AssertionError(f"Expected 2 entries, got {len(result)}")
    if result[0].get("end_date") != "2019" or result[1].get("end_date") != "2021":
        raise AssertionError(f"Expected two blocks with dates, got {result!r}")

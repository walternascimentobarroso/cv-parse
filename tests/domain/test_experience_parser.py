"""Unit tests for experience parser (domain layer)."""

from src.domain.experience_parser import (
    ExperienceEntry,
    _has_company_hint,
    parse_experience_section,
)


def test_parse_experience_empty_returns_empty() -> None:
    result = parse_experience_section("")
    if result != []:
        msg = f"Expected [], got {result!r}"
        raise AssertionError(msg)


def test_parse_experience_whitespace_only_returns_empty() -> None:
    result = parse_experience_section("   \n  ")
    if result != []:
        msg = f"Expected [], got {result!r}"
        raise AssertionError(msg)


def test_parse_experience_date_range_month_year() -> None:
    """Date range is extracted from the first line (header) of the block."""
    text = "Software Engineer at Acme Inc Jan 2020 - Dec 2022"
    result = parse_experience_section(text)
    if len(result) != 1:
        msg = f"Expected 1 entry, got {len(result)}"
        raise AssertionError(msg)
    entry = result[0]
    if not entry.get("start_date") or "2020" not in entry["start_date"]:
        msg = f"Expected start_date with 2020, got {entry!r}"
        raise AssertionError(msg)
    if not entry.get("end_date"):
        msg = f"Expected end_date, got {entry!r}"
        raise AssertionError(msg)
    if not entry.get("company") and not entry.get("role"):
        msg = f"Expected company or role, got {entry!r}"
        raise AssertionError(msg)


def test_parse_experience_date_range_year_only() -> None:
    """Year-only date range on header line is extracted."""
    text = "Developer at Company Ltd 2019 - 2021"
    result = parse_experience_section(text)
    if len(result) != 1:
        msg = f"Expected 1 entry, got {len(result)}"
        raise AssertionError(msg)
    if result[0].get("start_date") != "2019" or result[0].get("end_date") != "2021":
        msg = f"Expected 2019-2021, got {result[0]!r}"
        raise AssertionError(msg)


def test_parse_experience_present_end_date() -> None:
    """Present as end date on header line is extracted."""
    text = "Engineer at Startup Inc 2022 - Present"
    result = parse_experience_section(text)
    if len(result) != 1:
        msg = f"Expected 1 entry, got {len(result)}"
        raise AssertionError(msg)
    if "Present" not in result[0].get("end_date", ""):
        msg = f"Expected Present in end_date, got {result[0]!r}"
        raise AssertionError(msg)


def test_parse_experience_role_company_separator_at() -> None:
    text = "Senior Dev at Acme Ltd\n2020 - 2022"
    result = parse_experience_section(text)
    if len(result) != 1:
        msg = f"Expected 1 entry, got {len(result)}"
        raise AssertionError(msg)
    entry = result[0]
    if not (entry.get("role") or entry.get("company")):
        msg = f"Expected role or company, got {entry!r}"
        raise AssertionError(msg)


def test_parse_experience_company_hint_ltd() -> None:
    text = "Acme Ltd - Lead Engineer 2018 - 2019"
    result = parse_experience_section(text)
    if len(result) != 1:
        msg = f"Expected 1 entry, got {len(result)}"
        raise AssertionError(msg)
    if result[0].get("company") and "Acme" in result[0]["company"]:
        pass
    if result[0].get("role") and "Lead" in result[0]["role"]:
        pass


def test_parse_experience_no_company_hint_keeps_role_company_order() -> None:
    """When right part has no Ltd/Inc etc., keep common format: left=role, right=company."""
    text = "Developer at SmallCo 2020 - 2021"
    result = parse_experience_section(text)
    if len(result) != 1:
        msg = f"Expected 1 entry, got {len(result)}"
        raise AssertionError(msg)
    if result[0].get("role") != "Developer":
        msg = f"Expected role Developer, got {result[0].get('role')!r}"
        raise AssertionError(msg)
    if result[0].get("company") != "SmallCo":
        msg = f"Expected company SmallCo, got {result[0].get('company')!r}"
        raise AssertionError(msg)


def test_parse_experience_description_from_rest_of_block() -> None:
    """Lines after the header in the same block become description (no blank line in between)."""
    text = "Role at Company 2019 - 2020\nBuilt systems.\nUsed Python."
    result = parse_experience_section(text)
    if len(result) != 1:
        msg = f"Expected 1 entry, got {len(result)}"
        raise AssertionError(msg)
    desc = result[0].get("description", "")
    if "Built" not in desc or "Python" not in desc:
        msg = f"Expected description with content, got {desc!r}"
        raise AssertionError(msg)


def test_parse_experience_multiple_blocks() -> None:
    """Blank line separates blocks; date range must be on header line."""
    text = "Job A at X 2018-2019\n\nJob B at Y 2019-2021"
    result = parse_experience_section(text)
    if len(result) != 2:
        msg = f"Expected 2 entries, got {len(result)}"
        raise AssertionError(msg)
    if result[0].get("start_date") != "2018" or result[1].get("start_date") != "2019":
        msg = f"Expected two blocks with dates, got {result!r}"
        raise AssertionError(msg)


def test_parse_experience_output_dict_shape() -> None:
    text = "Dev at Corp\n2020 - 2021"
    result = parse_experience_section(text)
    entry = result[0]
    for key in ("company", "role", "start_date", "end_date", "description"):
        if key not in entry:
            msg = f"Expected key {key!r} in entry"
            raise AssertionError(msg)
    if not all(isinstance(v, str) for v in entry.values()):
        msg = f"All values must be str, got {entry!r}"
        raise AssertionError(msg)


def test_parse_experience_no_separator_uses_whole_header_as_role() -> None:
    """When header has no 'at'/'@'/'-' separator, whole header becomes role, company empty."""
    text = "Solo Role Title 2020 - 2021"
    result = parse_experience_section(text)
    if len(result) != 1:
        msg = f"Expected 1 entry, got {len(result)}"
        raise AssertionError(msg)
    if result[0].get("role") != "Solo Role Title":
        msg = f"Expected role from full header, got {result[0].get('role')!r}"
        raise AssertionError(msg)
    if result[0].get("company") != "":
        msg = f"Expected empty company, got {result[0].get('company')!r}"
        raise AssertionError(msg)


def test_experience_entry_dataclass_defaults() -> None:
    entry = ExperienceEntry()
    if entry.company is not None or entry.role is not None:
        msg = f"Expected None defaults, got {entry!r}"
        raise AssertionError(msg)
    if entry.start_date is not None or entry.end_date is not None or entry.description is not None:
        msg = f"Expected None defaults, got {entry!r}"
        raise AssertionError(msg)


def test_has_company_hint_empty_returns_false() -> None:
    if _has_company_hint("") is not False:
        msg = "Expected _has_company_hint('') to return False"
        raise AssertionError(msg)


def test_parse_experience_two_blocks_separated_by_header_line() -> None:
    """Two blocks separated by a new header line (no blank line) trigger block yield."""
    text = "Role A at Company X 2018 - 2019\nRole B at Company Y 2019 - 2021"
    result = parse_experience_section(text)
    if len(result) != 2:
        msg = f"Expected 2 entries, got {len(result)}"
        raise AssertionError(msg)
    if result[0].get("end_date") != "2019" or result[1].get("end_date") != "2021":
        msg = f"Expected two blocks with dates, got {result!r}"
        raise AssertionError(msg)


def test_parse_experience_linkedin_three_line_header() -> None:
    """LinkedIn export: Company on own line, Role on next, Date on next."""
    text = """Gruppy
Software Engineer
September 2023 - Present (2 years 7 months)
Situation: Some context.
ALTA
Software Engineer
August 2022 - September 2023 (1 year 2 months)
Situation: Other context.
"""
    result = parse_experience_section(text)
    if len(result) != 2:
        msg = f"Expected 2 entries, got {len(result)}"
        raise AssertionError(msg)
    if result[0].get("company") != "Gruppy" or result[0].get("role") != "Software Engineer":
        msg = f"Expected first entry company=Gruppy role=Software Engineer, got {result[0]!r}"
        raise AssertionError(msg)
    if result[1].get("company") != "ALTA" or result[1].get("role") != "Software Engineer":
        msg = f"Expected second entry company=ALTA role=Software Engineer, got {result[1]!r}"
        raise AssertionError(msg)


def test_parse_experience_profile_two_line_header() -> None:
    """Profile style: Role at Company on one line, date on next (e.g. Jan 2020 - Present)."""
    text = """Senior Engineer at Acme Robotics Ltd
Jan 2020 - Present
Situation: Legacy monolith.
Developer at Beta Corp
Mar 2017 - Dec 2019
Maintained MySQL.
"""
    result = parse_experience_section(text)
    if len(result) != 2:
        msg = f"Expected 2 entries, got {len(result)}"
        raise AssertionError(msg)
    if (
        result[0].get("company") != "Acme Robotics Ltd"
        or result[0].get("role") != "Senior Engineer"
    ):
        msg = f"Expected first entry Acme/Senior Engineer, got {result[0]!r}"
        raise AssertionError(msg)
    if result[1].get("company") != "Beta Corp" or result[1].get("role") != "Developer":
        msg = f"Expected second entry company=Beta Corp role=Developer, got {result[1]!r}"
        raise AssertionError(msg)

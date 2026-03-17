"""Unit tests for education parser (domain layer)."""

from src.domain.education_parser import (
    EducationEntry,
    parse_education_section,
)


def test_parse_education_empty_returns_empty() -> None:
    result = parse_education_section("")
    if result != []:
        raise AssertionError(f"Expected [], got {result!r}")


def test_parse_education_whitespace_only_returns_empty() -> None:
    result = parse_education_section("   \n  ")
    if result != []:
        raise AssertionError(f"Expected [], got {result!r}")


def test_parse_education_single_block_with_year_range() -> None:
    text = "University of London, BSc Computer Science 2018 - 2022"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    entry = result[0]
    if entry.get("start_year") != "2018" or entry.get("end_year") != "2022":
        raise AssertionError(f"Expected year range 2018-2022, got {entry!r}")
    if "London" not in (entry.get("institution") or ""):
        raise AssertionError(f"Expected institution with London, got {entry!r}")
    if not entry.get("degree"):
        raise AssertionError(f"Expected degree, got {entry!r}")


def test_parse_education_single_year() -> None:
    text = "MIT, PhD 2020"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("end_year") != "2020":
        raise AssertionError(f"Expected end_year 2020, got {result[0]!r}")


def test_parse_education_multiple_blocks() -> None:
    text = "University A, BSc 2015-2019\n\nCollege B, MSc 2019-2021"
    result = parse_education_section(text)
    if len(result) != 2:
        raise AssertionError(f"Expected 2 entries, got {len(result)}")
    if result[0].get("end_year") != "2019" or result[1].get("end_year") != "2021":
        raise AssertionError(f"Expected two blocks with years, got {result!r}")


def test_parse_education_no_years() -> None:
    text = "Some School, Diploma"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("start_year") != "" or result[0].get("end_year") != "":
        raise AssertionError(f"Expected empty years, got {result[0]!r}")


def test_parse_education_two_years_without_hyphen() -> None:
    """Two years in text without hyphen range hit the len(years) >= 2 branch."""
    text = "University of X, BSc 2015 2019"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("start_year") != "2015" or result[0].get("end_year") != "2019":
        raise AssertionError(f"Expected start 2015 end 2019, got {result[0]!r}")


def test_parse_education_institution_fallback_first_token() -> None:
    """When no institution/degree keyword, first token (before comma) becomes institution."""
    text = "Some School, 2020"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("institution") != "Some School":
        raise AssertionError(f"Expected first token as institution fallback, got {result[0]!r}")


def test_parse_education_degree_keywords() -> None:
    text = "State University, Master in CS 2018-2020"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if not result[0].get("degree"):
        raise AssertionError(f"Expected degree parsed, got {result[0]!r}")


def test_parse_education_output_dict_shape() -> None:
    text = "Institute of Tech, MBA 2010-2012"
    result = parse_education_section(text)
    entry = result[0]
    for key in ("institution", "degree", "start_year", "end_year"):
        if key not in entry:
            raise AssertionError(f"Expected key {key!r} in entry")
    if not all(isinstance(v, str) for v in entry.values()):
        raise AssertionError(f"All values must be str, got {entry!r}")


def test_education_entry_dataclass_defaults() -> None:
    entry = EducationEntry()
    if entry.institution is not None or entry.degree is not None:
        raise AssertionError(f"Expected None defaults, got {entry!r}")
    if entry.start_year is not None or entry.end_year is not None:
        raise AssertionError(f"Expected None year defaults, got {entry!r}")


def test_parse_education_two_blocks_separated_by_header_line() -> None:
    """Two blocks separated by header-like line (no blank line) trigger block yield."""
    text = "University A, BSc 2015-2019\nCollege B, MSc 2019-2021"
    result = parse_education_section(text)
    if len(result) != 2:
        raise AssertionError(f"Expected 2 entries, got {len(result)}")
    if result[0].get("end_year") != "2019" or result[1].get("end_year") != "2021":
        raise AssertionError(f"Expected two blocks with years, got {result!r}")


def test_parse_education_month_year_range() -> None:
    """Month-year range (e.g. Jan 2018 - Dec 2022) is parsed."""
    text = "State University, Master Jan 2018 - Dec 2022"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("start_year") != "2018" or result[0].get("end_year") != "2022":
        raise AssertionError(f"Expected 2018-2022 from month-year range, got {result[0]!r}")


def test_parse_education_header_only_years_no_text() -> None:
    """Only year range (no degree/institution) → entry with empty fields."""
    text = "2018 - 2022"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    if result[0].get("start_year") != "2018" or result[0].get("end_year") != "2022":
        raise AssertionError(f"Expected years 2018-2022, got {result[0]!r}")


def test_parse_education_degree_with_institution_word_and_rest_lines() -> None:
    """Degree ending with institution word + rest_lines splits degree and institution."""
    text = "Master University 2018 - 2022\nFaculty of Engineering"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    entry = result[0]
    if entry.get("degree") != "Master":
        raise AssertionError(f"Expected degree 'Master', got {entry.get('degree')!r}")
    if "University" not in (entry.get("institution") or ""):
        inst = entry.get("institution")
        raise AssertionError(
            "Expected institution to contain University and rest, "
            f"got {inst!r}",
        )


def test_parse_education_no_degree_or_institution_in_header_uses_first_token() -> None:
    """Header without degree keyword keeps tokens and does not split degree/institution."""
    text = "Institute of Tech 2018 - 2022\nSome Faculty"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    entry = result[0]
    if entry.get("degree") not in (None, ""):
        raise AssertionError(f"Expected empty degree, got {entry.get('degree')!r}")
    if "Some Faculty" not in (entry.get("institution") or ""):
        inst = entry.get("institution")
        raise AssertionError(
            "Expected rest lines in institution, "
            f"got {inst!r}",
        )


def test_parse_education_degree_without_institution_word_not_split() -> None:
    """Degree without trailing institution word should not be split."""
    text = "BSc Computer Science 2018-2022\nSome University"
    result = parse_education_section(text)
    if len(result) != 1:
        raise AssertionError(f"Expected 1 entry, got {len(result)}")
    entry = result[0]
    if "BSc" not in (entry.get("degree") or ""):
        raise AssertionError(f"Expected degree to contain 'BSc', got {entry.get('degree')!r}")

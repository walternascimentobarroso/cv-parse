from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


_YEAR_RANGE_PATTERN = re.compile(r"\b(?P<start>\d{4})\s*[-–]\s*(?P<end>\d{4})\b")
_MONTH_YEAR_RANGE_PATTERN = re.compile(
    r"\b(?P<start_mon>\w{3})\s+(?P<start>\d{4})\s*[-–]\s*(?P<end_mon>\w{3})\s+(?P<end>\d{4})\b"
)
_YEAR_PATTERN = re.compile(r"\b(?P<year>\d{4})\b")

_INSTITUTION_KEYWORDS = [
    "university",
    "college",
    "institute",
    "school",
    "polytechnic",
    "faculdade",
    "centro",
    "uniciv",
    "unyleya",
    "estácio",
    "cathedral",
]

_DEGREE_KEYWORDS = [
    "bachelor",
    "master",
    "phd",
    "doctor",
    "diploma",
    "bsc",
    "msc",
    "mba",
    "postgraduate",
    "lato sensu",
]


@dataclass
class EducationEntry:
    institution: str | None = None
    degree: str | None = None
    start_year: int | None = None
    end_year: int | None = None


def _iter_blocks(lines: list[str]) -> Iterable[list[str]]:
    """Split into blocks by blank lines or by lines that look like education headers (degree + date)."""
    block: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if block:
                yield block
                block = []
            continue
        if _line_looks_like_education_header(stripped) and block:
            yield block
            block = []
        block.append(line)
    if block:
        yield block


def _strip_year_segment(text: str) -> str:
    """Remove year range or month-year range from text; return the rest."""
    cleaned = _MONTH_YEAR_RANGE_PATTERN.sub("", text)
    cleaned = _YEAR_RANGE_PATTERN.sub("", cleaned)
    return cleaned.strip(" -–|,")


def _line_has_year_range(line: str) -> bool:
    if _YEAR_RANGE_PATTERN.search(line):
        return True
    if _MONTH_YEAR_RANGE_PATTERN.search(line):
        return True
    return False


def _line_looks_like_education_header(line: str) -> bool:
    """True if line has a year/month-year range and non-empty degree/institution text."""
    if not _line_has_year_range(line):
        return False
    rest = _strip_year_segment(line)
    return len(rest.strip()) >= 2


def _extract_years(text: str) -> tuple[int | None, int | None]:
    match = _MONTH_YEAR_RANGE_PATTERN.search(text)
    if match:
        return int(match.group("start")), int(match.group("end"))
    match = _YEAR_RANGE_PATTERN.search(text)
    if match:
        return int(match.group("start")), int(match.group("end"))

    years = [int(m.group("year")) for m in _YEAR_PATTERN.finditer(text)]
    if len(years) == 1:
        return None, years[0]
    if len(years) >= 2:
        return years[0], years[1]
    return None, None


def _looks_like_institution(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in _INSTITUTION_KEYWORDS)


def _looks_like_degree(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in _DEGREE_KEYWORDS)


def _build_education_entry(header_line: str, rest_lines: list[str]) -> EducationEntry:
    start_year, end_year = _extract_years(header_line)
    header_without_dates = _strip_year_segment(header_line)

    institution: str | None = None
    degree: str | None = None

    tokens = [t.strip() for t in re.split(r"[,-]", header_without_dates) if t.strip()]
    institution_from_header: str | None = None
    for token in tokens:
        if degree is None and _looks_like_degree(token):
            degree = token
            continue
        if institution_from_header is None and _looks_like_institution(token):
            institution_from_header = token

    if rest_lines:
        rest_joined = " ".join(part.strip() for part in rest_lines if part.strip()).strip()
        if degree and not institution_from_header:
            words = degree.split()
            if words and _looks_like_institution(words[-1]):
                institution_from_header = words[-1]
                degree = " ".join(words[:-1]).strip() or None
        institution = (f"{institution_from_header or ''} {rest_joined}".strip() if institution_from_header else rest_joined) or None
    else:
        institution = institution_from_header or (tokens[0] if tokens else None)

    return EducationEntry(
        institution=institution,
        degree=degree,
        start_year=start_year,
        end_year=end_year,
    )


def parse_education_section(text: str) -> list[dict]:
    if not text:
        return []

    lines = [line.rstrip() for line in text.splitlines()]
    entries: list[EducationEntry] = []

    for block in _iter_blocks(lines):
        header_line = block[0] if block else ""
        rest_lines = block[1:] if len(block) > 1 else []
        entries.append(_build_education_entry(header_line, rest_lines))

    return [
        {
            "institution": e.institution or "",
            "degree": e.degree or "",
            "start_year": str(e.start_year) if e.start_year is not None else "",
            "end_year": str(e.end_year) if e.end_year is not None else "",
        }
        for e in entries
    ]



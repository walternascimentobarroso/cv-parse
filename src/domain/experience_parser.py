from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable

_DATE_RANGE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?P<start>\b\w{3}\s+\d{4})\s*[-–]\s*(?P<end>\b\w{3}\s+\d{4}|\b[Pp]resent\b)"),
    re.compile(r"(?P<start>\b\d{4})\s*[-–]\s*(?P<end>\b\d{4}|\b[Pp]resent\b)"),
]

_ROLE_COMPANY_SEPARATORS = [" at ", " @ ", " - ", " – ", " | "]

_COMPANY_HINTS = [
    " ltd",
    " limited",
    " gmbh",
    " inc",
    " llc",
    " sas",
    " spa",
]


@dataclass
class ExperienceEntry:
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


def _extract_date_range(text: str) -> tuple[str | None, str | None]:
    for pattern in _DATE_RANGE_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group("start"), match.group("end")
    return None, None


def _strip_date_segment(text: str) -> str:
    cleaned = text
    for pattern in _DATE_RANGE_PATTERNS:
        cleaned = pattern.sub("", cleaned)
    return cleaned.strip(" -–|")


def _has_company_hint(text: str) -> bool:
    if not text:
        return False
    return any(hint in text.lower() for hint in _COMPANY_HINTS)


def _pick_company(
    role_candidate: str | None,
    company_candidate: str | None,
) -> tuple[str | None, str | None]:
    left = role_candidate.strip() if role_candidate else ""
    right = company_candidate.strip() if company_candidate else ""
    if right and _has_company_hint(right):
        return left or None, right or None
    if left and _has_company_hint(left):
        return right or None, left or None
    # Common format is "Role - Company"; without company hints keep left=role, right=company.
    return left or None, right or None


def _split_role_company(text: str) -> tuple[str | None, str | None]:
    value = text.strip()
    for sep in _ROLE_COMPANY_SEPARATORS:
        if sep in value:
            left, right = value.split(sep, 1)
            return _pick_company(left, right)
    return value or None, None


def _line_has_date_range(line: str) -> bool:
    start, end = _extract_date_range(line)
    return start is not None and end is not None


def _line_looks_like_experience_header(line: str) -> bool:
    """True if line has a date range and non-empty role/company text (not just the date)."""
    if not _line_has_date_range(line):
        return False
    header_part = _strip_date_segment(line).strip()
    if len(header_part) < 2:
        return False
    return True


def _iter_blocks(lines: list[str]) -> Iterable[list[str]]:
    """Split blocks by blank lines or experience-like headers (date + role/company)."""
    block: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if block:
                yield block
                block = []
            continue
        if _line_looks_like_experience_header(stripped) and block:
            yield block
            block = []
        block.append(line)
    if block:
        yield block


def _build_entry_from_block(block: list[str]) -> ExperienceEntry:
    header = block[0]
    rest_description = "\n".join(block[1:]).strip() or None

    start_date, end_date = _extract_date_range(header)
    header_without_dates = _strip_date_segment(header)
    role, company = _split_role_company(header_without_dates)

    return ExperienceEntry(
        company=company,
        role=role,
        start_date=start_date,
        end_date=end_date,
        description=rest_description,
    )


def parse_experience_section(text: str) -> list[dict]:
    if not text:
        return []

    lines = [line.rstrip() for line in text.splitlines()]
    entries = [_build_entry_from_block(block) for block in _iter_blocks(lines)]

    return [
        {
            "company": e.company or "",
            "role": e.role or "",
            "start_date": e.start_date or "",
            "end_date": e.end_date or "",
            "description": e.description or "",
        }
        for e in entries
    ]



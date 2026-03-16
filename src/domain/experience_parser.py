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


def _pick_company(role_candidate: str | None, company_candidate: str | None) -> tuple[str | None, str | None]:
    role = role_candidate.strip() if role_candidate else ""
    company = company_candidate.strip() if company_candidate else ""
    lowered_company = company.lower()
    if company and any(hint in lowered_company for hint in _COMPANY_HINTS):
        return role or None, company or None
    # Fallback: treat second token as role if hints do not match.
    return company or None, role or None


def _split_role_company(text: str) -> tuple[str | None, str | None]:
    value = text.strip()
    for sep in _ROLE_COMPANY_SEPARATORS:
        if sep in value:
            left, right = value.split(sep, 1)
            return _pick_company(left, right)
    return value or None, None


def _iter_blocks(lines: list[str]) -> Iterable[list[str]]:
    block: list[str] = []
    for line in lines:
        if not line.strip():
            if block:
                yield block
                block = []
            continue
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



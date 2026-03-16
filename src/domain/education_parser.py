from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable


_YEAR_RANGE_PATTERN = re.compile(r"\b(?P<start>\d{4})\s*[-–]\s*(?P<end>\d{4})\b")
_YEAR_PATTERN = re.compile(r"\b(?P<year>\d{4})\b")

_INSTITUTION_KEYWORDS = [
    "university",
    "college",
    "institute",
    "school",
    "polytechnic",
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
]


@dataclass
class EducationEntry:
    institution: str | None = None
    degree: str | None = None
    start_year: int | None = None
    end_year: int | None = None


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


def _extract_years(text: str) -> tuple[int | None, int | None]:
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


def _build_education_entry(header: str) -> EducationEntry:
    start_year, end_year = _extract_years(header)

    institution: str | None = None
    degree: str | None = None

    tokens = [t.strip() for t in re.split(r"[,-]", header) if t.strip()]
    for token in tokens:
        if institution is None and _looks_like_institution(token):
            institution = token
            continue
        if degree is None and _looks_like_degree(token):
            degree = token

    if institution is None and tokens:
        institution = tokens[0]

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
        header = " ".join(part for part in block if part.strip())
        entries.append(_build_education_entry(header))

    return [
        {
            "institution": e.institution or "",
            "degree": e.degree or "",
            "start_year": str(e.start_year) if e.start_year is not None else "",
            "end_year": str(e.end_year) if e.end_year is not None else "",
        }
        for e in entries
    ]



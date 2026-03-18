from __future__ import annotations

import re

_BULLET_CHARS = {"-", "*", "•", "●"}


def _strip_bullet(line: str) -> str:
    """Remove leading bullet characters and normalize whitespace."""
    line = line.strip()
    while line and line[0] in _BULLET_CHARS:
        line = line[1:].strip()
    return line


def _normalize_certification(text: str) -> str:
    """Collapse multiple spaces and strip."""
    return re.sub(r"\s+", " ", text).strip()


def parse_certifications_section(text: str) -> list[str]:
    if not text:
        return []

    results: list[str] = []
    current: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            if current:
                results.append(_normalize_certification(" ".join(current)))
                current = []
            continue

        content = _strip_bullet(line)
        if not content:
            continue

        if line[0] in _BULLET_CHARS:
            if current:
                results.append(_normalize_certification(" ".join(current)))
            current = [content]
            continue

        current.append(content)

    if current:
        results.append(_normalize_certification(" ".join(current)))

    return results

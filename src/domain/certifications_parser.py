from __future__ import annotations


def parse_certifications_section(text: str) -> list[str]:
    if not text:
        return []

    results: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        while line and line[0] in {"-", "*", "•"}:
            line = line[1:].strip()
        if not line:
            continue
        results.append(line)

    return results


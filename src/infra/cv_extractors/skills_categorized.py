"""Split Hard Skills vs Soft Skills subsections (heuristic)."""

from __future__ import annotations

import re


def extract_hard_and_soft_skills(skills_section_text: str) -> tuple[list[str], list[str]]:
    if not skills_section_text.strip():
        return [], []

    hard: list[str] = []
    soft: list[str] = []
    mode: str | None = None

    for raw in skills_section_text.splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower().rstrip(":")
        if re.match(r"^hard\s+skills?", low):
            mode = "hard"
            continue
        if re.match(r"^soft\s+skills?", low):
            mode = "soft"
            continue
        if re.match(r"^technical\s+skills?", low):
            mode = "hard"
            continue

        target = hard if mode != "soft" else soft
        if mode is None:
            target = hard

        for part in re.split(r"[,;|]", line):
            token = part.strip()
            if len(token) > 1:
                target.append(token)

    return hard, soft

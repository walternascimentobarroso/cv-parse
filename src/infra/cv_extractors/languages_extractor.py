"""Parse languages section into name + optional level."""

from __future__ import annotations

import re

_BULLET = re.compile(r"^[-*•●]\s*")


def extract_languages(text: str) -> list[dict[str, str | None]]:
    if not text.strip():
        return []
    out: list[dict[str, str | None]] = []
    seen: set[str] = set()

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        line = _BULLET.sub("", line).strip()
        if not line:
            continue
        parts = re.split(r"\s*(?:[:\u2014\u2013\-]|\()\s+", line, maxsplit=1)
        if len(parts) == 2 and 1 < len(parts[0]) < 45:
            name = parts[0].strip()
            level = parts[1].rstrip(")").strip()
            key = name.lower()
            if key not in seen:
                seen.add(key)
                out.append({"name": name, "level": level or None})
            continue
        if re.match(r"^[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s]{1,40}$", line):
            key = line.lower()
            if key not in seen:
                seen.add(key)
                out.append({"name": line, "level": None})
    return out

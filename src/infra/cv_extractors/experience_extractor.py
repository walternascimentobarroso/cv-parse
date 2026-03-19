"""Multi-block experience parsing + STAR merge. Regex/heuristics only."""

from __future__ import annotations

import re

from src.domain.experience_parser import parse_experience_section
from src.infra.logging_config import get_logger

_log = get_logger(__name__)

_DATE_RANGE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?P<start>\b\w{3}\s+\d{4})\s*[-–]\s*(?P<end>\b\w{3}\s+\d{4}|\b[Pp]resent\b)"),
    re.compile(r"(?P<start>\b\d{4})\s*[-–]\s*(?P<end>\b\d{4}|\b[Pp]resent\b)"),
]


def _star_bucket(line: str) -> str | None:
    s = line.strip()
    checks = [
        (r"^situation\s*[:.)]\s*", "situation"),
        (r"^task\s*[:.)]\s*", "task"),
        (r"^action\s*[:.)]\s*", "action"),
        (r"^result\s*[:.)]\s*", "result"),
        (r"^S\s*[:.)]\s*", "situation"),
        (r"^T\s*[:.)]\s*", "task"),
        (r"^A\s*[:.)]\s*", "action"),
        (r"^R\s*[:.)]\s*", "result"),
    ]
    for pat, bucket in checks:
        if re.match(pat, s, re.IGNORECASE):
            return bucket
    return None


def _star_rest(line: str) -> str:
    s = line.strip()
    for pat in (
        r"^(?:situation|task|action|result)\s*[:.)]\s*(.*)$",
        r"^[STAR]\s*[:.)]\s*(.*)$",
    ):
        m = re.match(pat, s, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return s


def _line_has_compact_date_range(line: str) -> bool:
    stripped = line.strip()
    if len(stripped) > 80:
        return False
    for pattern in _DATE_RANGE_PATTERNS:
        if pattern.search(stripped):
            return True
    return False


def _merge_role_line_with_following_dates(text: str) -> str:
    """Join 'Role at Co' + newline + '2020 - 2022' into one header line."""
    lines = text.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        cur = lines[i].rstrip()
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ""
        cur_stripped = cur.strip()
        if (
            cur_stripped
            and nxt
            and not _line_has_compact_date_range(cur_stripped)
            and _line_has_compact_date_range(nxt)
            and not nxt.startswith(("-", "*", "•", "●"))
            and len(nxt) < 50
        ):
            out.append(f"{cur_stripped} {nxt}")
            i += 2
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def _merge_star_description(description: str) -> tuple[str, list[str], list[str]]:
    if not description:
        return description, [], []
    has_star = any(_star_bucket(ln) is not None for ln in description.splitlines())
    if not has_star:
        return description, [], []

    situation: list[str] = []
    task: list[str] = []
    action: list[str] = []
    result: list[str] = []
    other: list[str] = []
    buckets: dict[str, list[str]] = {
        "situation": situation,
        "task": task,
        "action": action,
        "result": result,
    }
    current_key: str | None = None

    for line in description.splitlines():
        bucket = _star_bucket(line)
        if bucket is not None:
            current_key = bucket
            rest = _star_rest(line)
            if rest:
                buckets[bucket].append(rest)
            continue
        if line.strip():
            if current_key:
                buckets[current_key].append(line.strip())
            else:
                other.append(line.strip())

    ordered: list[str] = []
    for part in (situation, task, action, result):
        if part:
            ordered.append("\n".join(part))
    body = "\n\n".join(ordered) if ordered else description
    if other and other != situation + task + action + result:
        extra = "\n".join(other)
        body = f"{body}\n\n{extra}".strip() if body else extra

    responsibilities = [x for x in task + action if x]
    achievements = list(result)
    return body, responsibilities, achievements


def _entry_to_output(
    company: str,
    role: str,
    start: str,
    end: str,
    description: str,
) -> dict[str, object]:
    desc, resp, ach = _merge_star_description(description)
    out: dict[str, object] = {
        "company": company or "",
        "role": role or "",
        "start_date": start or "",
        "end_date": end or "",
        "description": desc or "",
    }
    if resp:
        out["responsibilities"] = resp
    if ach:
        out["achievements"] = ach
    return out


def parse_experience_multi(text: str) -> list[dict[str, object]]:
    """Parse experience section with multi-line date headers and STAR merging."""
    if not text.strip():
        return []
    normalized = _merge_role_line_with_following_dates(text)
    raw_entries = parse_experience_section(normalized)
    _log.debug("experience_blocks count=%s", len(raw_entries))
    return [
        _entry_to_output(
            str(e.get("company", "")),
            str(e.get("role", "")),
            str(e.get("start_date", "")),
            str(e.get("end_date", "")),
            str(e.get("description", "")),
        )
        for e in raw_entries
    ]

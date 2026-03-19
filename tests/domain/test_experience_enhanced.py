"""Enhanced experience extractor (multi-line headers + STAR)."""

from __future__ import annotations

from src.infra.cv_extractors.experience_extractor import parse_experience_multi


def test_parse_experience_multi_two_roles() -> None:
    text = """Senior at Acme Ltd
Jan 2020 - Dec 2021
Did work.

Junior at Beta Inc
2018 - 2019
More work.
"""
    r = parse_experience_multi(text)
    if len(r) != 2:
        msg = f"Expected 2 entries, got {len(r)}"
        raise AssertionError(msg)
    joined = " ".join(str(e.get("company", "")) for e in r).lower()
    if "acme" not in joined or "beta" not in joined:
        msg = f"Expected Acme and Beta, got {r!r}"
        raise AssertionError(msg)


def test_star_content_in_description() -> None:
    text = """Lead at Co Ltd
2020 - 2021
Situation: Slow app.
Task: Speed up.
Action: Cached queries.
Result: 2x faster.
"""
    r = parse_experience_multi(text)
    if not r:
        msg = "Expected one entry"
        raise AssertionError(msg)
    desc = str(r[0].get("description", ""))
    for frag in ("Slow app", "Speed up", "Cached", "2x faster"):
        if frag not in desc:
            msg = f"Missing {frag!r} in {desc!r}"
            raise AssertionError(msg)

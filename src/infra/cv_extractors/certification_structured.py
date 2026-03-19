"""Structured certification rows alongside legacy string list."""

from __future__ import annotations


def certification_details_from_strings(cert_strings: list[str]) -> list[dict[str, str | None]]:
    out: list[dict[str, str | None]] = []
    for s in cert_strings:
        text = s.strip()
        if not text:
            continue
        for sep in (" — ", " – ", " - ", " | ", ":", " —"):
            if sep in text and sep != ":":
                left, right = text.split(sep, 1)
                if len(right.strip()) > 1:
                    out.append({"name": left.strip(), "issuer": right.strip()})
                    break
        else:
            out.append({"name": text, "issuer": None})
    return out

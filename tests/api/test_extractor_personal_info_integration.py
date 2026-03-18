from __future__ import annotations

from typing import Any


def test_extract_includes_personal_info(client) -> None:  # type: ignore[no-untyped-def]
    content = (
        b"Ada Lovelace\n"
        b"ada.lovelace@example.com\n"
        b"https://www.linkedin.com/in/ada\n"
        b"github.com/ada\n"
        b"\n"
        b"Software engineer with experience in distributed systems.\n"
    )
    files: dict[str, tuple[str, bytes, str]] = {
        "file": ("cv.txt", content, "text/plain"),
    }
    response = client.post("/extract", files=files)
    if response.status_code != 200:
        raise AssertionError(f"Expected status 200, got {response.status_code}")
    body: dict[str, Any] = response.json()
    parsed = body.get("parsed_data") or {}
    personal_info = parsed.get("personal_info") or {}
    if personal_info.get("full_name") != "Ada Lovelace":
        raise AssertionError(f"Expected full_name, got {personal_info.get('full_name')!r}")
    if personal_info.get("email") != "ada.lovelace@example.com":
        raise AssertionError(f"Expected email, got {personal_info.get('email')!r}")


def test_existing_parsed_data_fields_preserved(client) -> None:  # type: ignore[no-untyped-def]
    content = (
        b"Experience\n"
        b"Engineer at Acme\n"
        b"\n"
        b"Education\n"
        b"MIT, BSc\n"
        b"\n"
        b"Skills\n"
        b"Python\n"
        b"\n"
        b"Certifications\n"
        b"AWS Certified\n"
    )
    files: dict[str, tuple[str, bytes, str]] = {
        "file": ("cv.txt", content, "text/plain"),
    }
    response = client.post("/extract", files=files)
    if response.status_code != 200:
        raise AssertionError(f"Expected status 200, got {response.status_code}")
    body: dict[str, Any] = response.json()
    parsed = body.get("parsed_data") or {}
    for key in ("experience", "education", "skills", "certifications"):
        if key not in parsed:
            raise AssertionError(f"Expected {key} in parsed_data, got keys {list(parsed.keys())}")


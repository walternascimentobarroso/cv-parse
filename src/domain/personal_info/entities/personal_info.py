from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class PersonalInfo:
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    summary: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LocationSummary:
    id: int
    name: str
    slug: str
    country: str
    is_active: bool


class LocationReaderPort(Protocol):
    def get_active_by_slug(self, slug: str) -> LocationSummary | None: ...

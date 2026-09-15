from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

from app.waitlist.infrastructure.orm.models import Guest, WaitlistEntry


@dataclass(frozen=True)
class LocationSummary:
    id: int
    organization_id: int
    slug: str
    country: str
    frequent_guest_threshold: int
    is_active: bool


class LocationReaderPort(Protocol):
    def get_active_by_slug(self, slug: str) -> LocationSummary | None: ...

    def get_by_id(self, location_id: int) -> LocationSummary | None: ...


class GuestRepositoryPort(Protocol):
    def find_by_phone(self, organization_id: int, phone_e164: str) -> Guest | None: ...

    def add(self, guest: Guest) -> None: ...

    def save(self, guest: Guest) -> None: ...


class WaitlistEntryRepositoryPort(Protocol):
    def add(self, entry: WaitlistEntry) -> None: ...

    def save(self, entry: WaitlistEntry) -> None: ...

    def get_by_id(self, entry_id: int) -> WaitlistEntry | None: ...

    def get_by_public_token(self, public_token: str) -> WaitlistEntry | None: ...

    def list_active_by_location(self, location_id: int) -> list[WaitlistEntry]: ...

    def count_waiting_at_or_above(self, location_id: int, sort_order: Decimal) -> int: ...

    def get_first_waiting(self, location_id: int, exclude_entry_id: int) -> WaitlistEntry | None: ...

    def get_successor(
        self, location_id: int, after_sort_order: Decimal, exclude_entry_id: int
    ) -> WaitlistEntry | None: ...

    def list_recent_completed_wait_minutes(self, location_id: int, limit: int = 20) -> list[int]: ...


class TableReadyNotifierPort(Protocol):
    def notify_table_ready(self, entry: WaitlistEntry) -> None: ...

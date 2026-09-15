from dataclasses import dataclass

from app.shared_kernel.domain.phone import normalize_phone_e164
from app.shared_kernel.ports.clock import ClockPort
from app.waitlist.application.ports.outbound import (
    GuestRepositoryPort,
    LocationReaderPort,
    WaitlistEntryRepositoryPort,
)
from app.waitlist.application.services.wait_time_estimator import estimate_wait_minutes
from app.waitlist.domain.errors import LocationNotFound
from app.waitlist.domain.sort_order import seed_sort_order
from app.waitlist.infrastructure.orm.models import Guest, WaitlistEntry


@dataclass(frozen=True)
class JoinWaitlistInput:
    location_slug: str
    guest_name: str
    phone_raw: str
    party_size: int


@dataclass(frozen=True)
class JoinWaitlistResult:
    entry: WaitlistEntry
    position: int
    estimated_wait_minutes: int


class JoinWaitlistUseCase:
    def __init__(
        self,
        locations: LocationReaderPort,
        guests: GuestRepositoryPort,
        entries: WaitlistEntryRepositoryPort,
        clock: ClockPort,
    ):
        self._locations = locations
        self._guests = guests
        self._entries = entries
        self._clock = clock

    def execute(self, input: JoinWaitlistInput) -> JoinWaitlistResult:
        location = self._locations.get_active_by_slug(input.location_slug)
        if location is None:
            raise LocationNotFound(input.location_slug)

        phone_e164 = normalize_phone_e164(input.phone_raw, default_region=location.country)
        now = self._clock.now()

        guest = self._guests.find_by_phone(location.organization_id, phone_e164)
        if guest is None:
            guest = Guest(
                organization_id=location.organization_id,
                phone_e164=phone_e164,
                display_name=input.guest_name,
                first_seen_at=now,
                last_seen_at=now,
                visit_count=1,
            )
            self._guests.add(guest)
        else:
            guest.display_name = input.guest_name
            guest.last_seen_at = now
            guest.visit_count += 1
            self._guests.save(guest)

        estimated_wait = estimate_wait_minutes(
            self._entries.list_recent_completed_wait_minutes(location.id)
        )

        entry = WaitlistEntry(
            organization_id=location.organization_id,
            location_id=location.id,
            guest_id=guest.id,
            guest_name_snapshot=input.guest_name,
            phone_snapshot=phone_e164,
            party_size=input.party_size,
            sort_order=seed_sort_order(now),
            joined_at=now,
            estimated_wait_minutes_at_join=estimated_wait,
        )
        self._entries.add(entry)

        position = self._entries.count_waiting_at_or_above(location.id, entry.sort_order)
        return JoinWaitlistResult(entry=entry, position=position, estimated_wait_minutes=estimated_wait)

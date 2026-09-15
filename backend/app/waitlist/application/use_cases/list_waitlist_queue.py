from dataclasses import dataclass

from app.waitlist.application.ports.outbound import LocationReaderPort, WaitlistEntryRepositoryPort
from app.waitlist.domain.errors import LocationNotFound
from app.waitlist.infrastructure.orm.models import WaitlistEntry


@dataclass(frozen=True)
class QueueEntryView:
    entry: WaitlistEntry
    position: int
    is_frequent_guest: bool


class ListWaitlistQueueUseCase:
    def __init__(self, locations: LocationReaderPort, entries: WaitlistEntryRepositoryPort):
        self._locations = locations
        self._entries = entries

    def execute(self, location_id: int) -> list[QueueEntryView]:
        location = self._locations.get_by_id(location_id)
        if location is None:
            raise LocationNotFound(location_id)

        active_entries = self._entries.list_active_by_location(location_id)
        return [
            QueueEntryView(
                entry=entry,
                position=index + 1,
                is_frequent_guest=entry.guest.visit_count >= location.frequent_guest_threshold,
            )
            for index, entry in enumerate(active_entries)
        ]

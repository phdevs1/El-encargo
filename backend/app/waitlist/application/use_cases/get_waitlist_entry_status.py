from dataclasses import dataclass

from app.shared_kernel.domain.enums import WaitlistStatus
from app.waitlist.application.ports.outbound import WaitlistEntryRepositoryPort
from app.waitlist.application.services.wait_time_estimator import estimate_wait_minutes
from app.waitlist.domain.errors import WaitlistEntryNotFound
from app.waitlist.infrastructure.orm.models import WaitlistEntry


@dataclass(frozen=True)
class WaitlistEntryStatusResult:
    entry: WaitlistEntry
    position: int | None
    estimated_wait_minutes: int | None


class GetWaitlistEntryStatusUseCase:
    def __init__(self, entries: WaitlistEntryRepositoryPort):
        self._entries = entries

    def execute(self, public_token: str) -> WaitlistEntryStatusResult:
        entry = self._entries.get_by_public_token(public_token)
        if entry is None:
            raise WaitlistEntryNotFound(public_token)

        if entry.status != WaitlistStatus.WAITING:
            return WaitlistEntryStatusResult(entry=entry, position=None, estimated_wait_minutes=None)

        position = self._entries.count_waiting_at_or_above(entry.location_id, entry.sort_order)
        estimated_wait = estimate_wait_minutes(
            self._entries.list_recent_completed_wait_minutes(entry.location_id)
        )
        return WaitlistEntryStatusResult(
            entry=entry, position=position, estimated_wait_minutes=estimated_wait
        )

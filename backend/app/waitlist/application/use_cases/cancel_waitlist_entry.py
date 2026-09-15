from app.shared_kernel.domain.enums import WaitlistStatus
from app.shared_kernel.ports.clock import ClockPort
from app.waitlist.application.ports.outbound import WaitlistEntryRepositoryPort
from app.waitlist.domain.errors import WaitlistEntryNotFound
from app.waitlist.domain.state_machine import assert_transition_allowed
from app.waitlist.infrastructure.orm.models import WaitlistEntry


class CancelWaitlistEntryUseCase:
    """Guest says 'Ya no voy' before being called: waiting -> cancelled."""

    def __init__(self, entries: WaitlistEntryRepositoryPort, clock: ClockPort):
        self._entries = entries
        self._clock = clock

    def execute(self, entry_id: int) -> WaitlistEntry:
        entry = self._entries.get_by_id(entry_id)
        if entry is None:
            raise WaitlistEntryNotFound(entry_id)
        return self._cancel(entry)

    def execute_by_public_token(self, public_token: str) -> WaitlistEntry:
        entry = self._entries.get_by_public_token(public_token)
        if entry is None:
            raise WaitlistEntryNotFound(public_token)
        return self._cancel(entry)

    def _cancel(self, entry: WaitlistEntry) -> WaitlistEntry:
        assert_transition_allowed(entry.status, WaitlistStatus.CANCELLED)
        entry.status = WaitlistStatus.CANCELLED
        entry.cancelled_at = self._clock.now()
        self._entries.save(entry)
        return entry

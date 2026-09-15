from app.shared_kernel.domain.enums import WaitlistStatus
from app.shared_kernel.ports.clock import ClockPort
from app.waitlist.application.ports.outbound import WaitlistEntryRepositoryPort
from app.waitlist.domain.errors import WaitlistEntryNotFound
from app.waitlist.domain.state_machine import assert_transition_allowed
from app.waitlist.infrastructure.orm.models import WaitlistEntry


class SeatWaitlistEntryUseCase:
    def __init__(self, entries: WaitlistEntryRepositoryPort, clock: ClockPort):
        self._entries = entries
        self._clock = clock

    def execute(self, entry_id: int) -> WaitlistEntry:
        entry = self._entries.get_by_id(entry_id)
        if entry is None:
            raise WaitlistEntryNotFound(entry_id)

        assert_transition_allowed(entry.status, WaitlistStatus.SEATED)
        entry.status = WaitlistStatus.SEATED
        entry.seated_at = self._clock.now()
        self._entries.save(entry)
        return entry

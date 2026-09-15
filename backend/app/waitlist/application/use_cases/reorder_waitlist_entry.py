from dataclasses import dataclass

from app.shared_kernel.domain.enums import WaitlistStatus
from app.waitlist.application.ports.outbound import WaitlistEntryRepositoryPort
from app.waitlist.domain.errors import InvalidReorderTarget, WaitlistEntryNotFound
from app.waitlist.domain.sort_order import compute_reordered_sort_order
from app.waitlist.infrastructure.orm.models import WaitlistEntry


@dataclass(frozen=True)
class ReorderInput:
    entry_id: int
    after_entry_id: int | None


class ReorderWaitlistEntryUseCase:
    def __init__(self, entries: WaitlistEntryRepositoryPort):
        self._entries = entries

    def execute(self, input: ReorderInput) -> WaitlistEntry:
        entry = self._entries.get_by_id(input.entry_id)
        if entry is None or entry.status != WaitlistStatus.WAITING:
            raise WaitlistEntryNotFound(input.entry_id)

        if input.after_entry_id == input.entry_id:
            raise InvalidReorderTarget(input.entry_id)

        if input.after_entry_id is None:
            lower = None
            upper = self._entries.get_first_waiting(entry.location_id, exclude_entry_id=entry.id)
        else:
            lower = self._entries.get_by_id(input.after_entry_id)
            if (
                lower is None
                or lower.location_id != entry.location_id
                or lower.status != WaitlistStatus.WAITING
            ):
                raise WaitlistEntryNotFound(input.after_entry_id)
            upper = self._entries.get_successor(
                entry.location_id, lower.sort_order, exclude_entry_id=entry.id
            )

        entry.sort_order = compute_reordered_sort_order(
            lower.sort_order if lower else None,
            upper.sort_order if upper else None,
            entry_id=entry.id,
        )
        self._entries.save(entry)
        return entry

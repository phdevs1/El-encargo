from app.shared_kernel.domain.enums import WaitlistStatus


class WaitlistDomainError(Exception):
    pass


class LocationNotFound(WaitlistDomainError):
    def __init__(self, identifier: str | int):
        self.identifier = identifier
        super().__init__(f"Location not found: {identifier!r}")


class WaitlistEntryNotFound(WaitlistDomainError):
    def __init__(self, identifier: str | int):
        self.identifier = identifier
        super().__init__(f"Waitlist entry not found: {identifier!r}")


class InvalidStateTransition(WaitlistDomainError):
    def __init__(self, current: WaitlistStatus, target: WaitlistStatus):
        self.current = current
        self.target = target
        super().__init__(f"Cannot move entry from {current.value} to {target.value}")


class InvalidReorderTarget(WaitlistDomainError):
    def __init__(self, entry_id: int):
        self.entry_id = entry_id
        super().__init__(f"Invalid reorder target for entry {entry_id}")


class SortOrderPrecisionExhausted(WaitlistDomainError):
    def __init__(self, entry_id: int):
        self.entry_id = entry_id
        super().__init__(f"Could not compute a sort order for entry {entry_id}: precision exhausted")

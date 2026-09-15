from app.shared_kernel.domain.enums import WaitlistStatus
from app.waitlist.domain.errors import InvalidStateTransition

_ALLOWED: dict[WaitlistStatus, set[WaitlistStatus]] = {
    WaitlistStatus.WAITING: {WaitlistStatus.CALLED, WaitlistStatus.CANCELLED},
    WaitlistStatus.CALLED: {WaitlistStatus.SEATED, WaitlistStatus.NO_SHOW},
}


def assert_transition_allowed(current: WaitlistStatus, target: WaitlistStatus) -> None:
    if target not in _ALLOWED.get(current, set()):
        raise InvalidStateTransition(current, target)

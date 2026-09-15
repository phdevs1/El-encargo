from typing import Callable

from fastapi import APIRouter

from app.waitlist.application.use_cases.call_waitlist_entry import CallWaitlistEntryUseCase
from app.waitlist.application.use_cases.cancel_waitlist_entry import CancelWaitlistEntryUseCase
from app.waitlist.application.use_cases.get_waitlist_entry_status import (
    GetWaitlistEntryStatusUseCase,
)
from app.waitlist.application.use_cases.join_waitlist import JoinWaitlistUseCase
from app.waitlist.application.use_cases.list_waitlist_queue import ListWaitlistQueueUseCase
from app.waitlist.application.use_cases.mark_no_show import MarkNoShowUseCase
from app.waitlist.application.use_cases.reorder_waitlist_entry import ReorderWaitlistEntryUseCase
from app.waitlist.application.use_cases.seat_waitlist_entry import SeatWaitlistEntryUseCase
from app.waitlist.infrastructure.http.guest_routes import build_guest_router
from app.waitlist.infrastructure.http.host_routes import build_host_router


def build_waitlist_guest_router(
    join_dep: Callable[..., JoinWaitlistUseCase],
    status_dep: Callable[..., GetWaitlistEntryStatusUseCase],
    cancel_dep: Callable[..., CancelWaitlistEntryUseCase],
) -> APIRouter:
    return build_guest_router(join_dep, status_dep, cancel_dep)


def build_waitlist_host_router(
    list_dep: Callable[..., ListWaitlistQueueUseCase],
    call_dep: Callable[..., CallWaitlistEntryUseCase],
    seat_dep: Callable[..., SeatWaitlistEntryUseCase],
    cancel_dep: Callable[..., CancelWaitlistEntryUseCase],
    no_show_dep: Callable[..., MarkNoShowUseCase],
    reorder_dep: Callable[..., ReorderWaitlistEntryUseCase],
) -> APIRouter:
    return build_host_router(list_dep, call_dep, seat_dep, cancel_dep, no_show_dep, reorder_dep)

from typing import Callable

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.shared_kernel.db.session import get_db
from app.waitlist.application.use_cases.call_waitlist_entry import CallWaitlistEntryUseCase
from app.waitlist.application.use_cases.cancel_waitlist_entry import CancelWaitlistEntryUseCase
from app.waitlist.application.use_cases.list_waitlist_queue import ListWaitlistQueueUseCase
from app.waitlist.application.use_cases.mark_no_show import MarkNoShowUseCase
from app.waitlist.application.use_cases.reorder_waitlist_entry import (
    ReorderInput,
    ReorderWaitlistEntryUseCase,
)
from app.waitlist.application.use_cases.seat_waitlist_entry import SeatWaitlistEntryUseCase
from app.waitlist.infrastructure.http.error_handling import handle_domain_errors
from app.waitlist.infrastructure.http.response_mappers import to_action_response
from app.waitlist.infrastructure.http.schemas import (
    ErrorResponse,
    HostQueueEntryResponse,
    HostQueueListResponse,
    ReorderRequest,
    WaitlistEntryActionResponse,
)

_STALE_OR_INVALID_TRANSITION = {
    409: {
        "model": ErrorResponse,
        "description": (
            "Either the entry can't move to this state from its current status, or "
            "someone else (the other tablet) already changed it — refetch and retry."
        ),
    },
}
_ENTRY_NOT_FOUND = {
    404: {"model": ErrorResponse, "description": "No waitlist entry matches `entry_id`."},
}


def build_host_router(
    list_dep: Callable[..., ListWaitlistQueueUseCase],
    call_dep: Callable[..., CallWaitlistEntryUseCase],
    seat_dep: Callable[..., SeatWaitlistEntryUseCase],
    cancel_dep: Callable[..., CancelWaitlistEntryUseCase],
    no_show_dep: Callable[..., MarkNoShowUseCase],
    reorder_dep: Callable[..., ReorderWaitlistEntryUseCase],
) -> APIRouter:
    router = APIRouter(tags=["waitlist-host"])

    @router.get(
        "/locations/{location_id:int}/waitlist-entries",
        response_model=HostQueueListResponse,
        summary="List a location's live queue (host tablet)",
        description=(
            "Powers screen 4. Returns `waiting` and `called` entries together, ordered "
            "by their queue position — a called entry keeps its row (with `called_at` "
            "set) until it's seated or marked no-show, matching the prototype's "
            "'Llamado HH:MM' badge behavior."
        ),
        responses={
            **_ENTRY_NOT_FOUND,  # raised when `location_id` itself doesn't exist
        },
    )
    @handle_domain_errors
    def list_queue(
        location_id: int,
        db: Session = Depends(get_db),
        uc: ListWaitlistQueueUseCase = Depends(list_dep),
    ) -> HostQueueListResponse:
        views = uc.execute(location_id)
        return HostQueueListResponse(
            entries=[
                HostQueueEntryResponse(
                    id=v.entry.id,
                    public_token=v.entry.public_token,
                    guest_name=v.entry.guest_name_snapshot,
                    phone_e164=v.entry.phone_snapshot,
                    party_size=v.entry.party_size,
                    status=v.entry.status,
                    position=v.position,
                    is_frequent_guest=v.is_frequent_guest,
                    joined_at=v.entry.joined_at,
                    called_at=v.entry.called_at,
                    estimated_wait_minutes_at_join=v.entry.estimated_wait_minutes_at_join,
                    version=v.entry.version,
                )
                for v in views
            ]
        )

    @router.post(
        "/waitlist-entries/{entry_id:int}/call",
        response_model=WaitlistEntryActionResponse,
        summary="Call a party (host taps 'Llamar')",
        description=(
            "Transitions `waiting -> called`, stamps `called_at`, and triggers a table-ready "
            "notification (WhatsApp/SMS in a later batch; currently just logged)."
        ),
        responses={**_ENTRY_NOT_FOUND, **_STALE_OR_INVALID_TRANSITION},
    )
    @handle_domain_errors
    def call_entry(
        entry_id: int,
        db: Session = Depends(get_db),
        uc: CallWaitlistEntryUseCase = Depends(call_dep),
    ) -> WaitlistEntryActionResponse:
        return to_action_response(uc.execute(entry_id))

    @router.post(
        "/waitlist-entries/{entry_id:int}/seat",
        response_model=WaitlistEntryActionResponse,
        summary="Seat a party (host taps 'Sentar')",
        description="Transitions `called -> seated` and stamps `seated_at`.",
        responses={**_ENTRY_NOT_FOUND, **_STALE_OR_INVALID_TRANSITION},
    )
    @handle_domain_errors
    def seat_entry(
        entry_id: int,
        db: Session = Depends(get_db),
        uc: SeatWaitlistEntryUseCase = Depends(seat_dep),
    ) -> WaitlistEntryActionResponse:
        return to_action_response(uc.execute(entry_id))

    @router.post(
        "/waitlist-entries/{entry_id:int}/cancel",
        response_model=WaitlistEntryActionResponse,
        summary="Cancel by internal id (host-side equivalent)",
        description=(
            "Transitions `waiting -> cancelled` and stamps `cancelled_at`. Only valid "
            "before the party has been called — use `/no-show` once they've been called. "
            "Guests use the token-keyed `POST /waitlist-entries/{public_token}/cancel` in "
            "`waitlist-guest` instead; this one is for host-side tooling operating on the "
            "internal id."
        ),
        responses={**_ENTRY_NOT_FOUND, **_STALE_OR_INVALID_TRANSITION},
    )
    @handle_domain_errors
    def cancel_entry(
        entry_id: int,
        db: Session = Depends(get_db),
        uc: CancelWaitlistEntryUseCase = Depends(cancel_dep),
    ) -> WaitlistEntryActionResponse:
        return to_action_response(uc.execute(entry_id))

    @router.post(
        "/waitlist-entries/{entry_id:int}/no-show",
        response_model=WaitlistEntryActionResponse,
        summary="Mark a called party as a no-show",
        description=(
            "Transitions `called -> no_show` and stamps `no_show_at`. Intended for the "
            "guest declining via WhatsApp ('Ya no voy' after being called) or a future "
            "timeout job — not yet exposed as a button in the host tablet prototype."
        ),
        responses={**_ENTRY_NOT_FOUND, **_STALE_OR_INVALID_TRANSITION},
    )
    @handle_domain_errors
    def mark_no_show(
        entry_id: int,
        db: Session = Depends(get_db),
        uc: MarkNoShowUseCase = Depends(no_show_dep),
    ) -> WaitlistEntryActionResponse:
        return to_action_response(uc.execute(entry_id))

    @router.patch(
        "/waitlist-entries/{entry_id:int}/reorder",
        response_model=WaitlistEntryActionResponse,
        summary="Reorder a waiting entry (host drags a row)",
        description=(
            "Moves the entry to immediately after `after_entry_id` in the waiting queue "
            "(or to the very top if `after_entry_id` is null), via a single-row fractional-"
            "indexing update — no other entry's `sort_order` is touched."
        ),
        responses={
            **_ENTRY_NOT_FOUND,
            409: {
                "model": ErrorResponse,
                "description": (
                    "Someone else already moved this entry (stale version), or the target "
                    "spot has been reordered into too many times and ran out of precision "
                    "between its neighbors."
                ),
            },
        },
    )
    @handle_domain_errors
    def reorder_entry(
        entry_id: int,
        body: ReorderRequest,
        db: Session = Depends(get_db),
        uc: ReorderWaitlistEntryUseCase = Depends(reorder_dep),
    ) -> WaitlistEntryActionResponse:
        result = uc.execute(ReorderInput(entry_id=entry_id, after_entry_id=body.after_entry_id))
        return to_action_response(result)

    return router

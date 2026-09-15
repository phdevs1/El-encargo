import uuid
from typing import Callable

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.shared_kernel.db.session import get_db
from app.waitlist.application.use_cases.cancel_waitlist_entry import CancelWaitlistEntryUseCase
from app.waitlist.application.use_cases.get_waitlist_entry_status import (
    GetWaitlistEntryStatusUseCase,
)
from app.waitlist.application.use_cases.join_waitlist import JoinWaitlistInput, JoinWaitlistUseCase
from app.waitlist.infrastructure.http.error_handling import handle_domain_errors
from app.waitlist.infrastructure.http.response_mappers import to_action_response
from app.waitlist.infrastructure.http.schemas import (
    ErrorResponse,
    JoinWaitlistRequest,
    JoinWaitlistResponse,
    WaitlistEntryActionResponse,
    WaitlistEntryStatusResponse,
)


def build_guest_router(
    join_dep: Callable[..., JoinWaitlistUseCase],
    status_dep: Callable[..., GetWaitlistEntryStatusUseCase],
    cancel_dep: Callable[..., CancelWaitlistEntryUseCase],
) -> APIRouter:
    router = APIRouter(tags=["waitlist-guest"])

    @router.post(
        "/locations/{slug}/waitlist-entries",
        response_model=JoinWaitlistResponse,
        status_code=201,
        summary="Join a location's waitlist",
        description=(
            "Called from the QR code at the door (screen 1). Creates a new waitlist "
            "ticket for the given location and returns a `public_token` the guest's "
            "browser should keep to poll their live status."
        ),
        responses={
            404: {"model": ErrorResponse, "description": "No active location matches `slug`."},
            422: {
                "model": ErrorResponse,
                "description": "`phone` could not be parsed as a valid number for the location's country.",
            },
        },
    )
    @handle_domain_errors
    def join_waitlist(
        slug: str,
        body: JoinWaitlistRequest,
        db: Session = Depends(get_db),
        uc: JoinWaitlistUseCase = Depends(join_dep),
    ) -> JoinWaitlistResponse:
        result = uc.execute(
            JoinWaitlistInput(
                location_slug=slug,
                guest_name=body.name,
                phone_raw=body.phone,
                party_size=body.party_size,
            )
        )
        return JoinWaitlistResponse(
            public_token=result.entry.public_token,
            position=result.position,
            estimated_wait_minutes=result.estimated_wait_minutes,
            status=result.entry.status,
            location_id=result.entry.location_id,
        )

    @router.get(
        "/waitlist-entries/{public_token:uuid}",
        response_model=WaitlistEntryStatusResponse,
        summary="Poll a guest's live waitlist status",
        description=(
            "Called repeatedly (short polling) by the guest's browser (screen 2) to "
            "animate their position and estimated wait as the queue advances, and to "
            "detect once the entry has moved to `called`/`seated`/`cancelled`/`no_show`."
        ),
        responses={
            404: {"model": ErrorResponse, "description": "No entry matches `public_token`."},
        },
    )
    @handle_domain_errors
    def get_status(
        public_token: uuid.UUID,
        db: Session = Depends(get_db),
        uc: GetWaitlistEntryStatusUseCase = Depends(status_dep),
    ) -> WaitlistEntryStatusResponse:
        result = uc.execute(str(public_token))
        return WaitlistEntryStatusResponse(
            public_token=result.entry.public_token,
            status=result.entry.status,
            position=result.position,
            estimated_wait_minutes=result.estimated_wait_minutes,
            party_size=result.entry.party_size,
            guest_name=result.entry.guest_name_snapshot,
        )

    @router.post(
        "/waitlist-entries/{public_token:uuid}/cancel",
        response_model=WaitlistEntryActionResponse,
        summary="Cancel before being called (guest taps 'Ya no voy')",
        description=(
            "Transitions `waiting -> cancelled`. Guest-safe: keyed by the unguessable "
            "`public_token`, never the internal sequential id used by the host routes."
        ),
        responses={
            404: {"model": ErrorResponse, "description": "No entry matches `public_token`."},
            409: {
                "model": ErrorResponse,
                "description": "Entry can no longer be cancelled from its current status.",
            },
        },
    )
    @handle_domain_errors
    def cancel_entry(
        public_token: uuid.UUID,
        db: Session = Depends(get_db),
        uc: CancelWaitlistEntryUseCase = Depends(cancel_dep),
    ) -> WaitlistEntryActionResponse:
        entry = uc.execute_by_public_token(str(public_token))
        return to_action_response(entry)

    return router

import asyncio

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.organizations.application.use_cases.get_location_summary import (
    GetLocationSummaryUseCase,
)
from app.organizations.composition import build_organizations_public_router
from app.organizations.infrastructure.orm.location_summary_reader import OrmLocationSummaryReader
from app.organizations.infrastructure.orm.waitlist_location_reader import OrmLocationReader
from app.shared_kernel.config import settings
from app.shared_kernel.db.session import SessionLocal, get_db
from app.shared_kernel.infrastructure.clock import SystemClock
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
from app.waitlist.composition import (
    build_waitlist_guest_router,
    build_waitlist_host_router,
    build_waitlist_ws_router,
)
from app.waitlist.infrastructure.http.response_mappers import to_host_queue_list_response
from app.waitlist.infrastructure.http.schemas import HostQueueListResponse
from app.waitlist.infrastructure.notifications.stub_notifier import LoggingTableReadyNotifier
from app.waitlist.infrastructure.orm.repositories import (
    SqlAlchemyGuestRepository,
    SqlAlchemyWaitlistEntryRepository,
)
from app.waitlist.infrastructure.websocket.connection_manager import broadcaster


OPENAPI_TAGS = [
    {
        "name": "organizations",
        "description": "Public location metadata (e.g. display name for the guest join screen).",
    },
    {
        "name": "waitlist-guest",
        "description": "Guest-facing endpoints reached from the door QR code (screens 1-2). Unauthenticated by design — protected only by the unguessable `public_token`.",
    },
    {
        "name": "waitlist-host",
        "description": "Host-tablet endpoints (screen 4). No authentication in this pilot batch — see project notes for the accepted risk.",
    },
]


def build_app() -> FastAPI:
    app = FastAPI(
        title="Restaurant Waitlist API",
        description=(
            "Digital waitlist for walk-in restaurant guests: QR check-in, live queue "
            "position, host tablet queue management, and table-ready notifications.\n\n"
            "This batch (Lote 1) covers the full guest+host happy path — join, poll "
            "status, list/call/seat/cancel/reorder — without WhatsApp/SMS delivery "
            "(stubbed) or the end-of-day report, which land in later batches."
        ),
        version="0.1.0",
        openapi_tags=OPENAPI_TAGS,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )

    def get_location_dep(db: Session = Depends(get_db)) -> GetLocationSummaryUseCase:
        return GetLocationSummaryUseCase(OrmLocationSummaryReader(db))

    def join_dep(db: Session = Depends(get_db)) -> JoinWaitlistUseCase:
        return JoinWaitlistUseCase(
            OrmLocationReader(db),
            SqlAlchemyGuestRepository(db),
            SqlAlchemyWaitlistEntryRepository(db),
            SystemClock(),
        )

    def status_dep(db: Session = Depends(get_db)) -> GetWaitlistEntryStatusUseCase:
        return GetWaitlistEntryStatusUseCase(SqlAlchemyWaitlistEntryRepository(db))

    def list_dep(db: Session = Depends(get_db)) -> ListWaitlistQueueUseCase:
        return ListWaitlistQueueUseCase(OrmLocationReader(db), SqlAlchemyWaitlistEntryRepository(db))

    def call_dep(db: Session = Depends(get_db)) -> CallWaitlistEntryUseCase:
        return CallWaitlistEntryUseCase(
            SqlAlchemyWaitlistEntryRepository(db), SystemClock(), LoggingTableReadyNotifier()
        )

    def seat_dep(db: Session = Depends(get_db)) -> SeatWaitlistEntryUseCase:
        return SeatWaitlistEntryUseCase(SqlAlchemyWaitlistEntryRepository(db), SystemClock())

    def cancel_dep(db: Session = Depends(get_db)) -> CancelWaitlistEntryUseCase:
        return CancelWaitlistEntryUseCase(SqlAlchemyWaitlistEntryRepository(db), SystemClock())

    def no_show_dep(db: Session = Depends(get_db)) -> MarkNoShowUseCase:
        return MarkNoShowUseCase(SqlAlchemyWaitlistEntryRepository(db), SystemClock())

    def reorder_dep(db: Session = Depends(get_db)) -> ReorderWaitlistEntryUseCase:
        return ReorderWaitlistEntryUseCase(SqlAlchemyWaitlistEntryRepository(db))

    def fetch_host_queue_snapshot(location_id: int) -> HostQueueListResponse:
        db = SessionLocal()
        try:
            uc = ListWaitlistQueueUseCase(OrmLocationReader(db), SqlAlchemyWaitlistEntryRepository(db))
            return to_host_queue_list_response(uc.execute(location_id))
        finally:
            db.close()

    broadcaster.configure(fetch_host_queue_snapshot)

    @app.on_event("startup")
    async def _bind_broadcaster_loop() -> None:
        broadcaster.bind_loop(asyncio.get_running_loop())

    app.include_router(build_organizations_public_router(get_location_dep))
    app.include_router(build_waitlist_guest_router(join_dep, status_dep, cancel_dep))
    app.include_router(
        build_waitlist_host_router(
            list_dep, call_dep, seat_dep, cancel_dep, no_show_dep, reorder_dep
        )
    )
    app.include_router(build_waitlist_ws_router())

    @app.get("/health", tags=["ops"], summary="Liveness check")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app

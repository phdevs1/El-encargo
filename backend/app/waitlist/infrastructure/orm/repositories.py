from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.shared_kernel.domain.enums import WaitlistStatus
from app.waitlist.infrastructure.orm.models import Guest, WaitlistEntry


class SqlAlchemyGuestRepository:
    def __init__(self, db: Session):
        self._db = db

    def find_by_phone(self, organization_id: int, phone_e164: str) -> Guest | None:
        return self._db.execute(
            select(Guest).where(
                Guest.organization_id == organization_id, Guest.phone_e164 == phone_e164
            )
        ).scalar_one_or_none()

    def add(self, guest: Guest) -> None:
        self._db.add(guest)
        self._db.flush()

    def save(self, guest: Guest) -> None:
        self._db.flush()


class SqlAlchemyWaitlistEntryRepository:
    def __init__(self, db: Session):
        self._db = db

    def add(self, entry: WaitlistEntry) -> None:
        self._db.add(entry)
        self._db.flush()

    def save(self, entry: WaitlistEntry) -> None:
        self._db.flush()

    def get_by_id(self, entry_id: int) -> WaitlistEntry | None:
        return self._db.get(WaitlistEntry, entry_id)

    def get_by_public_token(self, public_token: str) -> WaitlistEntry | None:
        return self._db.execute(
            select(WaitlistEntry).where(WaitlistEntry.public_token == public_token)
        ).scalar_one_or_none()

    def list_active_by_location(self, location_id: int) -> list[WaitlistEntry]:
        return list(
            self._db.execute(
                select(WaitlistEntry)
                .where(
                    WaitlistEntry.location_id == location_id,
                    WaitlistEntry.status.in_([WaitlistStatus.WAITING, WaitlistStatus.CALLED]),
                )
                .order_by(WaitlistEntry.sort_order.asc())
            )
            .scalars()
            .all()
        )

    def count_waiting_at_or_above(self, location_id: int, sort_order: Decimal) -> int:
        return self._db.execute(
            select(func.count())
            .select_from(WaitlistEntry)
            .where(
                WaitlistEntry.location_id == location_id,
                WaitlistEntry.status == WaitlistStatus.WAITING,
                WaitlistEntry.sort_order <= sort_order,
            )
        ).scalar_one()

    def get_first_waiting(self, location_id: int, exclude_entry_id: int) -> WaitlistEntry | None:
        return self._db.execute(
            select(WaitlistEntry)
            .where(
                WaitlistEntry.location_id == location_id,
                WaitlistEntry.status == WaitlistStatus.WAITING,
                WaitlistEntry.id != exclude_entry_id,
            )
            .order_by(WaitlistEntry.sort_order.asc())
            .limit(1)
        ).scalar_one_or_none()

    def get_successor(
        self, location_id: int, after_sort_order: Decimal, exclude_entry_id: int
    ) -> WaitlistEntry | None:
        return self._db.execute(
            select(WaitlistEntry)
            .where(
                WaitlistEntry.location_id == location_id,
                WaitlistEntry.status == WaitlistStatus.WAITING,
                WaitlistEntry.sort_order > after_sort_order,
                WaitlistEntry.id != exclude_entry_id,
            )
            .order_by(WaitlistEntry.sort_order.asc())
            .limit(1)
        ).scalar_one_or_none()

    def list_recent_completed_wait_minutes(self, location_id: int, limit: int = 20) -> list[int]:
        rows = self._db.execute(
            select(WaitlistEntry.joined_at, WaitlistEntry.seated_at)
            .where(
                WaitlistEntry.location_id == location_id,
                WaitlistEntry.status == WaitlistStatus.SEATED,
                WaitlistEntry.seated_at.isnot(None),
            )
            .order_by(WaitlistEntry.seated_at.desc())
            .limit(limit)
        ).all()
        return [int((seated - joined).total_seconds() // 60) for joined, seated in rows]

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.organizations.infrastructure.orm.models import Location
from app.waitlist.application.ports.outbound import LocationSummary


class OrmLocationReader:
    """Implements waitlist's LocationReaderPort against the organizations module's tables."""

    def __init__(self, db: Session):
        self._db = db

    def get_active_by_slug(self, slug: str) -> LocationSummary | None:
        location = self._db.execute(
            select(Location).where(Location.slug == slug, Location.is_active.is_(True))
        ).scalar_one_or_none()
        return self._to_summary(location) if location else None

    def get_by_id(self, location_id: int) -> LocationSummary | None:
        location = self._db.get(Location, location_id)
        return self._to_summary(location) if location else None

    @staticmethod
    def _to_summary(location: Location) -> LocationSummary:
        return LocationSummary(
            id=location.id,
            organization_id=location.organization_id,
            slug=location.slug,
            country=location.country,
            frequent_guest_threshold=location.frequent_guest_threshold,
            is_active=location.is_active,
        )

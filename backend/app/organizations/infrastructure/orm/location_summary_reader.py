from sqlalchemy import select
from sqlalchemy.orm import Session

from app.organizations.application.ports.outbound import LocationSummary
from app.organizations.infrastructure.orm.models import Location


class OrmLocationSummaryReader:
    """Implements organizations' own LocationReaderPort — distinct from
    waitlist_location_reader.py, which implements waitlist's port instead."""

    def __init__(self, db: Session):
        self._db = db

    def get_active_by_slug(self, slug: str) -> LocationSummary | None:
        location = self._db.execute(
            select(Location).where(Location.slug == slug, Location.is_active.is_(True))
        ).scalar_one_or_none()
        if location is None:
            return None
        return LocationSummary(
            id=location.id,
            name=location.name,
            slug=location.slug,
            country=location.country,
            is_active=location.is_active,
        )

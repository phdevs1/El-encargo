from app.organizations.application.ports.outbound import LocationReaderPort, LocationSummary
from app.organizations.domain.errors import LocationNotFound


class GetLocationSummaryUseCase:
    def __init__(self, locations: LocationReaderPort):
        self._locations = locations

    def execute(self, slug: str) -> LocationSummary:
        location = self._locations.get_active_by_slug(slug)
        if location is None:
            raise LocationNotFound(slug)
        return location

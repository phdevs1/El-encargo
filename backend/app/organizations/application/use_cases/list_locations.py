from app.organizations.application.ports.outbound import LocationReaderPort, LocationSummary


class ListLocationsUseCase:
    def __init__(self, locations: LocationReaderPort):
        self._locations = locations

    def execute(self) -> list[LocationSummary]:
        return self._locations.list_active()

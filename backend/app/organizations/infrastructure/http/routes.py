from typing import Callable

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.organizations.application.use_cases.get_location_summary import (
    GetLocationSummaryUseCase,
)
from app.organizations.application.use_cases.list_locations import ListLocationsUseCase
from app.organizations.infrastructure.http.error_handling import handle_domain_errors
from app.organizations.infrastructure.http.schemas import (
    ErrorResponse,
    LocationListItem,
    LocationListResponse,
    LocationSummaryResponse,
)
from app.shared_kernel.db.session import get_db


def build_organizations_router(
    get_location_dep: Callable[..., GetLocationSummaryUseCase],
    list_locations_dep: Callable[..., ListLocationsUseCase],
) -> APIRouter:
    router = APIRouter(tags=["organizations"])

    @router.get(
        "/locations",
        response_model=LocationListResponse,
        summary="List active locations",
        description=(
            "All active locations across every organization — e.g. to build a "
            "location picker, or to look up a `location_id` for the host tablet "
            "URL without querying the database directly."
        ),
    )
    @handle_domain_errors
    def list_locations(
        db: Session = Depends(get_db),
        uc: ListLocationsUseCase = Depends(list_locations_dep),
    ) -> LocationListResponse:
        locations = uc.execute()
        return LocationListResponse(
            locations=[
                LocationListItem(id=loc.id, name=loc.name, slug=loc.slug, country=loc.country)
                for loc in locations
            ]
        )

    @router.get(
        "/locations/{slug}",
        response_model=LocationSummaryResponse,
        summary="Get a location's public display info",
        description=(
            "Used by the guest join screen (screen 1) to show the location's name "
            "before the guest fills in the form."
        ),
        responses={
            404: {"model": ErrorResponse, "description": "No active location matches `slug`."},
        },
    )
    @handle_domain_errors
    def get_location(
        slug: str,
        db: Session = Depends(get_db),
        uc: GetLocationSummaryUseCase = Depends(get_location_dep),
    ) -> LocationSummaryResponse:
        location = uc.execute(slug)
        return LocationSummaryResponse(name=location.name, slug=location.slug, country=location.country)

    return router

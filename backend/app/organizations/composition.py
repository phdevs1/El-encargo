from typing import Callable

from fastapi import APIRouter

from app.organizations.application.use_cases.get_location_summary import (
    GetLocationSummaryUseCase,
)
from app.organizations.application.use_cases.list_locations import ListLocationsUseCase
from app.organizations.infrastructure.http.routes import build_organizations_router


def build_organizations_public_router(
    get_location_dep: Callable[..., GetLocationSummaryUseCase],
    list_locations_dep: Callable[..., ListLocationsUseCase],
) -> APIRouter:
    return build_organizations_router(get_location_dep, list_locations_dep)

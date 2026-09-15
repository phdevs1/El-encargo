from typing import Callable

from fastapi import APIRouter

from app.organizations.application.use_cases.get_location_summary import (
    GetLocationSummaryUseCase,
)
from app.organizations.infrastructure.http.routes import build_organizations_router


def build_organizations_public_router(
    get_location_dep: Callable[..., GetLocationSummaryUseCase],
) -> APIRouter:
    return build_organizations_router(get_location_dep)

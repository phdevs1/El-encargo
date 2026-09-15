from pydantic import BaseModel, ConfigDict


class ErrorResponse(BaseModel):
    """Shape of every error body returned by the organizations API."""

    detail: str


class LocationSummaryResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "La Terraza Azul", "slug": "la-terraza-azul", "country": "PE"}
        }
    )

    name: str
    slug: str
    country: str


class LocationListItem(BaseModel):
    id: int
    name: str
    slug: str
    country: str


class LocationListResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "locations": [
                    {"id": 1, "name": "La Terraza Azul", "slug": "la-terraza-azul", "country": "PE"},
                    {"id": 2, "name": "Cuatro Vientos", "slug": "cuatro-vientos", "country": "PE"},
                    {"id": 3, "name": "Casa Mediterránea", "slug": "casa-mediterranea", "country": "CL"},
                ]
            }
        }
    )

    locations: list[LocationListItem]

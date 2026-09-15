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

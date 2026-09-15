from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.shared_kernel.domain.enums import WaitlistStatus


class ErrorResponse(BaseModel):
    """Shape of every error body returned by the waitlist API (see `error_handling.py`)."""

    detail: str


class JoinWaitlistRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"name": "Carla", "phone": "+51 987 654 321", "party_size": 4}
        }
    )

    name: str = Field(min_length=1, max_length=255, description="Guest's name, as typed at the door.")
    phone: str = Field(
        min_length=6,
        max_length=20,
        description=(
            "Guest's phone number in any common format. Parsed and normalized to E.164 "
            "using the location's country as the default region (e.g. a 9-digit number "
            "at a Peru location is assumed to be a PE mobile number)."
        ),
    )
    party_size: int = Field(gt=0, le=30, description="Number of people in the party.")


class JoinWaitlistResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "public_token": "24e6699a-cb81-4981-9aa8-1dc32fcbab06",
                "position": 1,
                "estimated_wait_minutes": 25,
                "status": "waiting",
            }
        }
    )

    public_token: str = Field(
        description=(
            "Opaque, unguessable id for this guest's ticket. Used for every subsequent "
            "guest-facing call — save it (e.g. in the QR landing page's URL) to poll status."
        )
    )
    position: int = Field(description="1-based position in the waiting queue right now.")
    estimated_wait_minutes: int = Field(description="Estimated wait in minutes, at the moment of joining.")
    status: WaitlistStatus
    location_id: int = Field(
        description="Internal id of the location this ticket belongs to (used internally to broadcast live queue updates)."
    )


class WaitlistEntryStatusResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "public_token": "24e6699a-cb81-4981-9aa8-1dc32fcbab06",
                "status": "waiting",
                "position": 1,
                "estimated_wait_minutes": 22,
                "party_size": 4,
                "guest_name": "Carla",
            }
        }
    )

    public_token: str
    status: WaitlistStatus
    position: int | None = Field(
        default=None,
        description="1-based position in the waiting queue. Null once the entry is no longer 'waiting' (called/seated/cancelled/no_show).",
    )
    estimated_wait_minutes: int | None = Field(
        default=None,
        description=(
            "Estimated wait in minutes, recomputed from current conditions on every poll. "
            "Null once the entry is no longer 'waiting'."
        ),
    )
    party_size: int
    guest_name: str


class HostQueueEntryResponse(BaseModel):
    id: int = Field(description="Internal entry id — used for host actions (call/seat/cancel/reorder).")
    public_token: str
    guest_name: str
    phone_e164: str
    party_size: int
    status: WaitlistStatus = Field(description="Only 'waiting' or 'called' entries appear in this list.")
    position: int = Field(description="1-based rank within the combined waiting+called queue.")
    is_frequent_guest: bool = Field(
        description="True when this guest's phone has joined this location's queue at or above the location's frequent-guest threshold."
    )
    joined_at: datetime
    called_at: datetime | None = Field(
        default=None, description="Set once the host taps 'Llamar'; null while still 'waiting'."
    )
    estimated_wait_minutes_at_join: int | None
    version: int = Field(
        description="Optimistic-lock token. Unrelated to this response's use, but useful for debugging 409 conflicts."
    )


class HostQueueListResponse(BaseModel):
    entries: list[HostQueueEntryResponse]


class ReorderRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"after_entry_id": 12}})

    after_entry_id: int | None = Field(
        default=None,
        description=(
            "Id of the entry this one should be placed immediately after within the "
            "waiting queue. Use null to move this entry to the very top of the queue."
        ),
    )


class WaitlistEntryActionResponse(BaseModel):
    id: int
    status: WaitlistStatus
    version: int = Field(description="Bumped by this action; pass-through for optimistic-lock debugging.")
    called_at: datetime | None = None
    seated_at: datetime | None = None
    cancelled_at: datetime | None = None
    no_show_at: datetime | None = None
    sort_order: str | None = Field(
        default=None, description="Entry's current ordering key, as a decimal string (only meaningful after a reorder)."
    )
    location_id: int = Field(
        description="Internal id of the location this entry belongs to (used internally to broadcast live queue updates)."
    )

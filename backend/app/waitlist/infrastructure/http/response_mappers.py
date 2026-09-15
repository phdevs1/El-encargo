from app.waitlist.infrastructure.http.schemas import WaitlistEntryActionResponse
from app.waitlist.infrastructure.orm.models import WaitlistEntry


def to_action_response(entry: WaitlistEntry) -> WaitlistEntryActionResponse:
    return WaitlistEntryActionResponse(
        id=entry.id,
        status=entry.status,
        version=entry.version,
        called_at=entry.called_at,
        seated_at=entry.seated_at,
        cancelled_at=entry.cancelled_at,
        no_show_at=entry.no_show_at,
        sort_order=str(entry.sort_order),
    )

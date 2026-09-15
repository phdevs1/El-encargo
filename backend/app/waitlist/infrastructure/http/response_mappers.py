from app.waitlist.application.use_cases.list_waitlist_queue import QueueEntryView
from app.waitlist.infrastructure.http.schemas import (
    HostQueueEntryResponse,
    HostQueueListResponse,
    WaitlistEntryActionResponse,
)
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
        location_id=entry.location_id,
    )


def to_host_queue_list_response(views: list[QueueEntryView]) -> HostQueueListResponse:
    return HostQueueListResponse(
        entries=[
            HostQueueEntryResponse(
                id=v.entry.id,
                public_token=v.entry.public_token,
                guest_name=v.entry.guest_name_snapshot,
                phone_e164=v.entry.phone_snapshot,
                party_size=v.entry.party_size,
                status=v.entry.status,
                position=v.position,
                is_frequent_guest=v.is_frequent_guest,
                joined_at=v.entry.joined_at,
                called_at=v.entry.called_at,
                estimated_wait_minutes_at_join=v.entry.estimated_wait_minutes_at_join,
                version=v.entry.version,
            )
            for v in views
        ]
    )

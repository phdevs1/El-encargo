import logging

from app.waitlist.infrastructure.orm.models import WaitlistEntry

logger = logging.getLogger(__name__)


class LoggingTableReadyNotifier:
    """Stand-in for the real WhatsApp/SMS adapter (built in a later batch)."""

    def notify_table_ready(self, entry: WaitlistEntry) -> None:
        logger.info(
            "table_ready_notification_stub entry_id=%s phone=%s", entry.id, entry.phone_snapshot
        )

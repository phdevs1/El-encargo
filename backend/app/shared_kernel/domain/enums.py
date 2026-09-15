import enum


class NotificationChannel(str, enum.Enum):
    WHATSAPP = "whatsapp"
    SMS = "sms"


class WaitlistStatus(str, enum.Enum):
    WAITING = "waiting"
    CALLED = "called"
    SEATED = "seated"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class GuestResponse(str, enum.Enum):
    ON_THE_WAY = "on_the_way"
    NOT_COMING = "not_coming"


class NotificationPurpose(str, enum.Enum):
    TABLE_READY = "table_ready"


class NotificationStatus(str, enum.Enum):
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    REJECTED = "rejected"


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"

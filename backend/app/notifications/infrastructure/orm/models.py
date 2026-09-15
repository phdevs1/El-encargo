from datetime import datetime
from decimal import Decimal

from sqlalchemy import CHAR, DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.shared_kernel.db.base import Base, TimestampMixin
from app.shared_kernel.domain.enums import (
    NotificationChannel,
    NotificationPurpose,
    NotificationStatus,
)


class NotificationAttempt(TimestampMixin, Base):
    __tablename__ = "notification_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    waitlist_entry_id: Mapped[int] = mapped_column(
        ForeignKey("waitlist_entries.id"), nullable=False, index=True
    )

    channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, native_enum=True, length=20), nullable=False
    )
    purpose: Mapped[NotificationPurpose] = mapped_column(
        Enum(NotificationPurpose, native_enum=True, length=30),
        nullable=False,
        default=NotificationPurpose.TABLE_READY,
    )
    template_key: Mapped[str] = mapped_column(String(100), nullable=False)
    template_external_id: Mapped[str | None] = mapped_column(String(150))

    country: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    locale: Mapped[str] = mapped_column(String(10), nullable=False, default="es")
    recipient_phone_e164: Mapped[str] = mapped_column(String(20), nullable=False)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_message_id: Mapped[str | None] = mapped_column(String(150))

    status: Mapped[NotificationStatus] = mapped_column(
        Enum(NotificationStatus, native_enum=True, length=20),
        nullable=False,
        default=NotificationStatus.QUEUED,
    )
    failure_reason: Mapped[str | None] = mapped_column(String(255))

    cost_amount: Mapped[Decimal | None] = mapped_column(Numeric(10, 4))
    cost_currency: Mapped[str | None] = mapped_column(CHAR(3))

    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    guest_response_action: Mapped[str | None] = mapped_column(String(50))

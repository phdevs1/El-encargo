from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, JSON, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared_kernel.db.base import Base, TimestampMixin
from app.shared_kernel.domain.enums import EmailStatus


class LocationDailyReport(TimestampMixin, Base):
    __tablename__ = "location_daily_reports"
    __table_args__ = (UniqueConstraint("location_id", "report_date"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False, index=True
    )
    report_date: Mapped[date] = mapped_column(Date, nullable=False)

    joined_count: Mapped[int] = mapped_column(Integer, nullable=False)
    seated_count: Mapped[int] = mapped_column(Integer, nullable=False)
    left_without_seating_count: Mapped[int] = mapped_column(Integer, nullable=False)
    no_show_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_wait_minutes: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))

    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    email_status: Mapped[EmailStatus] = mapped_column(
        Enum(EmailStatus, native_enum=True, length=20),
        nullable=False,
        default=EmailStatus.PENDING,
    )
    email_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    email_recipients: Mapped[list | None] = mapped_column(JSON)

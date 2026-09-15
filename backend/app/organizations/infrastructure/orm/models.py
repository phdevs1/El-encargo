from sqlalchemy import Boolean, CHAR, Enum, ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared_kernel.db.base import Base, TimestampMixin
from app.shared_kernel.domain.enums import NotificationChannel


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    country_default: Mapped[str | None] = mapped_column(CHAR(2))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    locations: Mapped[list["Location"]] = relationship(back_populates="organization")


class Location(TimestampMixin, Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    country: Mapped[str] = mapped_column(CHAR(2), nullable=False)
    timezone: Mapped[str] = mapped_column(String(64), nullable=False)
    whatsapp_business_number: Mapped[str | None] = mapped_column(String(32))
    default_notification_channel: Mapped[NotificationChannel] = mapped_column(
        Enum(NotificationChannel, native_enum=True, length=20),
        nullable=False,
        default=NotificationChannel.WHATSAPP,
    )
    no_show_timeout_minutes: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=20)
    frequent_guest_threshold: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=2)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    organization: Mapped["Organization"] = relationship(back_populates="locations")

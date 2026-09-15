import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.shared_kernel.db.base import Base, TimestampMixin
from app.shared_kernel.domain.enums import GuestResponse, WaitlistStatus


class Guest(TimestampMixin, Base):
    __tablename__ = "guests"
    __table_args__ = (UniqueConstraint("organization_id", "phone_e164"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    phone_e164: Mapped[str] = mapped_column(String(20), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    visit_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    entries: Mapped[list["WaitlistEntry"]] = relationship(back_populates="guest")


class WaitlistEntry(TimestampMixin, Base):
    __tablename__ = "waitlist_entries"
    __table_args__ = (
        CheckConstraint("party_size > 0", name="party_size_positive"),
        Index("ix_waitlist_entries_location_status_sort", "location_id", "status", "sort_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    public_token: Mapped[str] = mapped_column(
        String(36), nullable=False, unique=True, default=lambda: str(uuid.uuid4())
    )
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False, index=True
    )
    guest_id: Mapped[int] = mapped_column(ForeignKey("guests.id"), nullable=False)

    guest_name_snapshot: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_snapshot: Mapped[str] = mapped_column(String(20), nullable=False)
    party_size: Mapped[int] = mapped_column(SmallInteger, nullable=False)

    status: Mapped[WaitlistStatus] = mapped_column(
        Enum(WaitlistStatus, native_enum=True, length=20),
        nullable=False,
        default=WaitlistStatus.WAITING,
    )
    # 20 integer digits comfortably fit epoch-millis seeds (13 digits) with
    # room to spare; 10 fractional digits give fractional-indexing reorders
    # many successive midpoint insertions before precision is exhausted.
    sort_order: Mapped[Decimal] = mapped_column(Numeric(30, 10), nullable=False, index=True)

    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, index=True)
    called_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    seated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    no_show_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))

    guest_response: Mapped[GuestResponse | None] = mapped_column(
        Enum(GuestResponse, native_enum=True, length=20)
    )
    estimated_wait_minutes_at_join: Mapped[int | None] = mapped_column(SmallInteger)

    # Optimistic-locking token: SQLAlchemy bumps this on every UPDATE and
    # raises StaleDataError if a concurrent writer already moved it on
    # (guards against two host tablets calling/seating the same party).
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    guest: Mapped["Guest"] = relationship(back_populates="entries")

    __mapper_args__ = {"version_id_col": version}


class WaitlistEventLog(Base):
    __tablename__ = "waitlist_event_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    waitlist_entry_id: Mapped[int] = mapped_column(
        ForeignKey("waitlist_entries.id"), nullable=False, index=True
    )
    location_id: Mapped[int] = mapped_column(
        ForeignKey("locations.id"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, index=True
    )
    event_metadata: Mapped[dict | None] = mapped_column(JSON)

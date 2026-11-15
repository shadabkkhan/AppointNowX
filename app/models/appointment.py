from enum import Enum
from decimal import Decimal
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    CheckConstraint,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.doctor import Doctor



class AppointmentStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"



class PaymentStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"



class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"

    __table_args__ = (
    CheckConstraint(
        "patient_age IS NULL OR patient_age BETWEEN 0 AND 130",
        name="ck_appointment_age",
    ),
    CheckConstraint(
        "scheduled_end > scheduled_start",
        name="ck_appointment_duration",
    ),
    CheckConstraint(
        "amount >= 0",
        name="ck_appointment_amount",
    ),

    Index(
        "ix_appointments_doctor_start",
        "doctor_id",
        "scheduled_start",
    ),
    Index(
        "ix_appointments_org_start",
        "organization_id",
        "scheduled_start",
    ),
    Index(
        "ix_appointments_status_start",
        "status",
        "scheduled_start",
    ),
)

    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="RESTRICT"),
        nullable=False
    )

    patient_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    patient_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    patient_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    patient_age: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    appointment_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    scheduled_start:Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    scheduled_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )

    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    status: Mapped[AppointmentStatus] = mapped_column(
        SQLAlchemyEnum(
            AppointmentStatus,
            native_enum=True,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        default=AppointmentStatus.PENDING,
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )

    payment_status: Mapped[PaymentStatus] = mapped_column(
        SQLAlchemyEnum(
            PaymentStatus,
            native_enum=True,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        default=PaymentStatus.NOT_REQUIRED,
        nullable=False,
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    cancellation_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )


    organization: Mapped["Organization"] = relationship(
        back_populates="appointments",
    )

    doctors: Mapped["Doctor"] = relationship(
        back_populates="appointments",
    )
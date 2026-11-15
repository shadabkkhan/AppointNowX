from sqlalchemy import (
    ForeignKey,
    Integer,
    String,
    JSON,
    Boolean,
    Numeric,
    CheckConstraint,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.user import User
    from app.models.appointment import Appointment
    from app.models.ai_conversation import AIConversation

from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

class Doctor(TimestampMixin, Base):
    __tablename__ = "doctors"

    __table_args__ = (
        CheckConstraint(
            "years_of_experience is NULL OR years_of_experience >= 0",
            name="ck_doctors_experience_non_negetive",
        ),

        CheckConstraint(
            "amount IS NULL OR amount >= 0",
            name="ck_doctors_consultation_fee_non_negetive"
        ),

        CheckConstraint(
            "max_patient_per_day IS NULL OR max_patient_per_day > 0",
            name="ck_doctors_daily_patient_limit_positive",
        ),

        CheckConstraint(
            "CHAR_LENGTH(TRIM(speciality)) >= 2",
            name="ck_doctors_speciality_min_length",
        ),

        CheckConstraint(
            "CHAR_LENGTH(TRIM(name)) >= 2",
            name="ck_doctors_name_min_length",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    speciality: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    sub_specialities: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    qualifications: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    years_of_experience: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    bio: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    profile_image: Mapped[str | None] = mapped_column(
        String(500), 
        nullable=True,
    )

    languages: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    timezone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    locations: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    appointment_type: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    appointment_duration: Mapped[dict | None] = mapped_column(
        JSON,
        nullable= True,
    )

    working_schedule: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    break_times: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
    )

    max_patient_per_day: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    walk_in: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    amount: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True,
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        default="INR",
        nullable=False,
    )

    calendar_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    on_leave: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    leaves: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True,
    )

    notification_preferences: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    users: Mapped["User"] = relationship(
        back_populates="doctors"
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="doctors"
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="doctors"
    )

    ai_conversations: Mapped[list["AIConversation"]] = relationship(
        back_populates="doctors"
    )

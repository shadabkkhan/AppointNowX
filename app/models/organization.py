from enum import Enum

from sqlalchemy import Boolean, Enum as SQLAlchemyEnum
from sqlalchemy import Integer, JSON, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.doctor import Doctor
    from app.models.appointment import Appointment
    from app.models.ai_conversation import AIConversation

class OrganizationType(str, Enum):
    CLINIC = "clinic"
    HOSPITAL = "hospital"


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    __table_args__ = (
        CheckConstraint(
            "CHAR_LENGTH(TRIM(name)) >= 2",
            name="ck_organizations_name_not_empty",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    type: Mapped[OrganizationType] = mapped_column(
        SQLAlchemyEnum(
            OrganizationType,
            native_enum=True,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    locations: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True
    )
    
    appointment_type: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    appointment_duration: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    call_phone_number: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    whatsapp_enabled: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        nullable=False,
    )

    chat_enabled: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        nullable=False,
    )

    call_enabled: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        nullable=False,
    )

    users: Mapped[list["User"]] = relationship(
        back_populates="organization"
    )

    doctors: Mapped[list["Doctor"]] = relationship(
        back_populates="organization"
    )

    appointments: Mapped[list["Appointment"]] = relationship(
        back_populates="organization",
    )

    ai_conversations: Mapped[list["AIConversation"]] = relationship(
        back_populates="organization"
    )



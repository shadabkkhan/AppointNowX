from enum import Enum
from decimal import Decimal
from sqlalchemy import (
    Integer,
    Boolean,
    String,
    Text,
    JSON,
    Enum as SQLAlchemyEnum,
    DateTime,
    UniqueConstraint,
    Index,
    Numeric,
    ForeignKey
)
from app.db.base import TimestampMixin, Base
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.doctor import Doctor


from sqlalchemy.orm import Mapped, mapped_column, relationship

class ConversationChannel(str, Enum):
    WHATSAPP = "whatsapp"
    CALL = "call"
    CHAT = "chat"
    MANUAL = "manual"


class ConversationStatus(str, Enum):
    OPEN = "open"
    RESOLVED = "resolved"
    COMPLETED = "completed"


class ConversationIntent(str, Enum):
    BOOK_APPOINTMENT = "book_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    RESCHEDULE = "reschedule"
    GENERAL_INQUIRY = "general_inquiry"
    EMERGENCY = "emergency"
    FOLLOW_UP = "follow_up"
    ROOT_CANAL = "root_canal"
    OTHER = "other"


class AIConversation(TimestampMixin, Base):
    __tablename__ = "ai_conversations"

    __table_args__ = (

        UniqueConstraint(
            "organization_id", "patient_phone", name="uq_ai_conversation_org_patient_phone",
        ),

        Index(
            "ix_ai_conversation_org_status",
            "organization_id",
            "status",
        ),

        Index(
            "ix_ai_conversation_org_updated_at",
            "organization_id",
            "updated_at",
        ),

        Index(
            "ix_ai_conversations_org_doctor",
            "organization_id",
            "doctor_id",
        ),

    )

    id: Mapped[int] = mapped_column(
        Integer,
        autoincrement=True,
        primary_key=True,
        nullable=False
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
    )

    doctor_id: Mapped[int] = mapped_column(
        ForeignKey("doctors.id", ondelete="RESTRICT"),
        nullable=True
    )

    patient_phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    channel: Mapped[ConversationChannel] = mapped_column(
        SQLAlchemyEnum(
            ConversationChannel,
            native_enum=True,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,
    )

    status: Mapped[ConversationStatus] = mapped_column(
        SQLAlchemyEnum(
            ConversationStatus, 
            native_enum = True,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        default=ConversationStatus.OPEN,
        nullable=False,
    )

    intent: Mapped[ConversationIntent] = mapped_column(
        SQLAlchemyEnum(
            ConversationIntent,
            native_enum=True,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=True,
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    transcript: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True
    )

    is_resolved: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    is_emergency: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    follow_up: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True
    )

    tags: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="ai_conversations"
    )
    
    doctors: Mapped["Doctor"] = relationship(
        back_populates="ai_conversations"
    )

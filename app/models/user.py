from enum import Enum

from sqlalchemy import (
    Boolean, 
    Enum as SQLAlchemyEnum,
    ForeignKey,
    Integer,
    JSON,
    String,
    UniqueConstraint,
    CheckConstraint,
    Index
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.organization import Organization
    from app.models.doctor import Doctor

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    DOCTOR = "doctor"

class User(TimestampMixin, Base):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "CHAR_LENGTH(TRIM(email)) > 0",
            name="ck_users_email_not_empty",
        ),

        CheckConstraint(
            "CHAR_LENGTH(TRIM(hash_password)) > 0",
            name="ck_users_password_hash_not_empty",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    hash_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    role: Mapped[UserRole] = mapped_column(
        SQLAlchemyEnum(
            UserRole,
            native_enum=True,
            values_callable=lambda enum_class: [
                member.value for member in enum_class
            ],
        ),
        nullable=False,

    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False
    )

    permissions: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    organization: Mapped["Organization"] = relationship(
        back_populates="users"
    )

    doctors: Mapped["Doctor | None"] = relationship(
        back_populates="users",
        uselist=False
    )
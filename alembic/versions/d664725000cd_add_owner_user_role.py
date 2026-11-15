"""add owner user role

Revision ID: d664725000cd
Revises: f8c1f8dd7086
Create Date: 2026-11-15 14:26:25.071365
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "d664725000cd"
down_revision: Union[str, Sequence[str], None] = "f8c1f8dd7086"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add owner to the users.role enum (appended last for an in-place change)."""

    op.alter_column(
        "users",
        "role",
        existing_type=mysql.ENUM(
            "user", "admin", "doctor",
            collation="utf8mb4_unicode_ci",
        ),
        type_=mysql.ENUM(
            "user", "admin", "doctor", "owner",
            collation="utf8mb4_unicode_ci",
        ),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Remove owner from the users.role enum."""

    # MySQL strict mode rejects shrinking an ENUM while rows still use the removed value.
    op.execute("UPDATE users SET role = 'admin' WHERE role = 'owner'")

    op.alter_column(
        "users",
        "role",
        existing_type=mysql.ENUM(
            "user", "admin", "doctor", "owner",
            collation="utf8mb4_unicode_ci",
        ),
        type_=mysql.ENUM(
            "user", "admin", "doctor",
            collation="utf8mb4_unicode_ci",
        ),
        existing_nullable=False,
    )
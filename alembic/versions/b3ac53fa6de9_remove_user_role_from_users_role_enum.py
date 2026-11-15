"""remove user role from users role enum

Revision ID: b3ac53fa6de9
Revises: d664725000cd
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = "b3ac53fa6de9"
down_revision: Union[str, Sequence[str], None] = "d664725000cd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Remove 'user' from users.role. Refuses to run if any row still uses it."""

    bind = op.get_bind()
    remaining = bind.execute(
        sa.text("SELECT COUNT(*) FROM users WHERE role = 'user'")
    ).scalar_one()
    if remaining:
        raise RuntimeError(
            f"Cannot remove 'user' role: {remaining} user(s) still have it. "
            "Reassign them first."
        )

    op.alter_column(
        "users",
        "role",
        existing_type=mysql.ENUM(
            "user", "admin", "doctor", "owner",
            collation="utf8mb4_unicode_ci",
        ),
        type_=mysql.ENUM(
            "owner", "admin", "doctor",
            collation="utf8mb4_unicode_ci",
        ),
        existing_nullable=False,
    )


def downgrade() -> None:
    """Restore the 'user' value to the enum."""

    op.alter_column(
        "users",
        "role",
        existing_type=mysql.ENUM(
            "owner", "admin", "doctor",
            collation="utf8mb4_unicode_ci",
        ),
        type_=mysql.ENUM(
            "user", "admin", "doctor", "owner",
            collation="utf8mb4_unicode_ci",
        ),
        existing_nullable=False,
    )
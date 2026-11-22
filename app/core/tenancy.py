from typing import TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)

# Organization isolation rules
# 1. organization_id always comes from current_user, never request data.
# 2. Every query on an organization owned table filters by organization_id.
# 3. Another organizations record returns 404 never 403.
# 4. Create records with organization_id from current_user.

async def get_organization_scoped(
        session: AsyncSession,
        model: type[ModelType],
        object_id: int,
        organization_id: int,
) -> ModelType | None:
    if not hasattr(model, "organization_id"):
        raise ValueError(
            f"{model.__name__} does not support organization validation"
        )

    statement = select(model).where(
        model.id == object_id,
        model.organization_id == organization_id,
    )

    result = await session.scalar(statement)

    return result
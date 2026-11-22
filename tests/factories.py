from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationType

from uuid import uuid4

from app.core.security import hash_password
from app.models.user import User, UserRole

TEST_PASSWORD = "TestPassword123!"
TEST_PASSWORD_HASH = hash_password(TEST_PASSWORD)

async def make_organization(
    session: AsyncSession,
    **overrides: object,
) -> Organization:
    attributes: dict[str, object] = {
        "name": "Test Clinic",
        "type": OrganizationType.CLINIC,
        "timezone": "Asia/Kolkata",
    }

    attributes.update(overrides)

    organization = Organization(**attributes)

    session.add(organization)
    await session.flush()

    return organization


async def make_user(
    session: AsyncSession,
    *,
    organization: Organization | None = None,
    role: UserRole = UserRole.DOCTOR,
    **overrides: object,
) -> User:
    if organization is None:
        organization = await make_organization(session)

    attributes: dict[str, object] = {
        "email": f"test-{uuid4().hex}@example.com",
        "hash_password": TEST_PASSWORD_HASH,
        "role": role,
        "is_active": True,
        "is_verified": True,
        "organization": organization,
    }

    attributes.update(overrides)

    user = User(**attributes)

    session.add(user)
    await session.flush()

    return user
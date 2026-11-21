from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization, OrganizationType


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
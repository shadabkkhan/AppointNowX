import pytest

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from tests.factories import make_organization


@pytest.mark.anyio
async def test_database_connection_uses_test_database(
    db_session: AsyncSession,
) -> None:
    result = await db_session.execute(text("SELECT DATABASE()"))

    database_name = result.scalar_one()

    assert database_name.endswith("_test")


@pytest.mark.anyio
async def test_commit_inside_test_is_rolled_back(
    db_session: AsyncSession,
) -> None:
    organization = await make_organization(db_session)
    organization_id = organization.id

    await db_session.commit()

    saved_organization = await db_session.get(
        Organization,
        organization_id,
    )

    assert saved_organization is not None
    assert saved_organization.name == "Test Clinic"


@pytest.mark.anyio
async def test_organizations_table_starts_empty(
    db_session: AsyncSession,
) -> None:
    result = await db_session.execute(
        select(func.count()).select_from(Organization)
    )

    organization_count = result.scalar_one()

    assert organization_count == 0
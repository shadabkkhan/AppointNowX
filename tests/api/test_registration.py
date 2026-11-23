from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User, UserRole
from tests.factories import TEST_PASSWORD_HASH

pytestmark = pytest.mark.anyio

def make_registration_payload() -> dict[str, str]:
    return {
        "organization_name": "AppointNowX Test Clinic",
        "organization_type": "clinic",
        "timezone": "Asia/Kolkata",
        "owner_email": f"owner-{uuid4().hex}@example.com",
        "owner_password": "TestPassword123!",
        "owner_phone": "+919876543210",
    }


async def test_register_creates_organization_and_owner(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    payload = make_registration_payload()

    response = await client.post(
        "/api/v1/auth/register",
        json=payload
    )

    assert response.status_code == 201
    body = response.json()

    organization = body["organization"]
    owner = body["owner"]

    assert organization["name"] == payload["organization_name"]
    assert organization["type"] == payload["organization_type"]
    assert organization["timezone"] == payload["timezone"]

    assert owner["email"] == payload["owner_email"]
    assert owner["phone"] == payload["owner_phone"]
    assert owner["role"] == UserRole.OWNER.value

    assert "hash_password" not in owner
    assert "permissions" not in owner
    assert "is_active" not in owner
    assert "is_verified" not in owner

    assert payload["owner_password"] not in response.text
    assert TEST_PASSWORD_HASH not in response.text

    organization_result = await db_session.execute(
        select(Organization).where(
            Organization.id == organization["id"]
        )
    )

    saved_organization = organization_result.scalar_one_or_none()

    assert saved_organization is not None
    assert saved_organization.name == payload["organization_name"]

    owner_result = await db_session.execute(
        select(User).where(
            User.id == owner["id"]
        )
    )

    saved_owner = owner_result.scalar_one_or_none()

    assert saved_owner is not None
    assert saved_owner.email == payload["owner_email"]
    assert saved_owner.role == UserRole.OWNER
    assert saved_owner.organization_id == saved_organization.id



async def test_register_rejects_duplicate_email(
    client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    payload = make_registration_payload()

    await client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    duplicate_payload = make_registration_payload()
    duplicate_payload["owner_email"] = payload["owner_email"]

    response = await client.post(
        "/api/v1/auth/register",
        json=duplicate_payload,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "An account with this email already exists."
    )


async def test_register_validation_error_does_not_leak_password(
    client: AsyncClient,
) -> None:
    payload = make_registration_payload()
    payload["owner_email"] = "invalid-email"

    response = await client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 422

    assert payload["owner_password"] not in response.text
    assert TEST_PASSWORD_HASH not in response.text

    errors = response.json()["detail"]

    assert errors
    for error in errors:
        assert "input" not in error
        assert "ctx" not in error


async def test_register_rejects_client_supplied_role_and_organization_id(
    client: AsyncClient,
) -> None:
    payload = make_registration_payload()

    payload["role"] = "admin"
    payload["organization_id"] = 999

    response = await client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert response.status_code == 422

    errors = response.json()["detail"]
    rejected_fields = {
        error["loc"][-1]
        for error in errors
    }

    assert "role" in rejected_fields
    assert "organization_id" in rejected_fields

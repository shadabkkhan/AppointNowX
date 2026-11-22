
from datetime import timedelta

import pytest
from httpx import AsyncClient

from app.core.tokens import create_access_token
from app.models.user import UserRole
from tests.factories import TEST_PASSWORD_HASH, make_user

from tests.factories import (
    TEST_PASSWORD_HASH,
    make_organization,
    make_user,
)
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.anyio


@pytest.mark.parametrize(
    "headers",
    [
        {},
        {"Authorization": "Basic abc"},
    ],
)
async def test_auth_me_rejects_missing_or_non_bearer_credentials(
    client: AsyncClient,
    headers: dict[str, str],
) -> None:
    response = await client.get(
        "/api/v1/auth/me",
        headers=headers,
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_auth_me_rejects_garbage_token(
    client: AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_auth_me_rejects_expired_token(
    client: AsyncClient,
    db_session,
) -> None:
    user = await make_user(db_session)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
        expires_delta=timedelta(seconds=-1),
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


async def test_auth_me_returns_current_user(
    client: AsyncClient,
    db_session,
) -> None:
    user = await make_user(db_session)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == user.id
    assert body["email"] == user.email
    assert body["role"] == user.role.value
    assert body["organization_id"] == user.organization_id
    assert body["is_active"] is True
    assert body["phone"] == user.phone

    assert "hash_password" not in body
    assert TEST_PASSWORD_HASH not in response.text
    assert "permissions" not in body


async def test_auth_me_rejects_nonexistent_user(
    client: AsyncClient,
    db_session,
) -> None:
    user = await make_user(db_session)

    token = create_access_token(
        user_id=user.id + 100000,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


async def test_auth_me_rejects_inactive_user(
    client: AsyncClient,
    db_session,
) -> None:
    user = await make_user(
        db_session,
        is_active=False,
    )

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Account is disabled"


async def test_auth_me_rejects_stale_role(
    client: AsyncClient,
    db_session,
) -> None:
    user = await make_user(
        db_session,
        role=UserRole.ADMIN,
    )

    token = create_access_token(
        user_id=user.id,
        role=UserRole.ADMIN,
        organization_id=user.organization_id,
    )

    user.role = UserRole.DOCTOR
    await db_session.flush()

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


async def test_auth_me_rejects_stale_organization(
    client: AsyncClient,
    db_session,
) -> None:
    user = await make_user(db_session)

    original_organization_id = user.organization_id

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=original_organization_id,
    )

    new_organization = await make_organization(db_session)

    user.organization_id = new_organization.id
    await db_session.flush()

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401

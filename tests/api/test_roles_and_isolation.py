from collections.abc import AsyncIterator

import pytest
from fastapi import Depends, FastAPI, HTTPException
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.tokens import create_access_token
from app.db.session import get_db
from app.models.user import User, UserRole
from tests.factories import make_user, make_organization
from app.core.deps import get_current_user, require_roles
from app.core.tenancy import get_organization_scoped
from app.models.organization import Organization

async def test_owner_can_access_owner_only_route(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user = await make_user(db_session, role=UserRole.OWNER)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await test_client.get(
        "/test/owner-only",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


async def test_admin_cannot_access_owner_only_route(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user = await make_user(db_session, role=UserRole.ADMIN)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await test_client.get(
        "/test/owner-only",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


async def test_doctor_cannot_access_owner_only_route(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user = await make_user(db_session, role=UserRole.DOCTOR)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await test_client.get(
        "/test/owner-only",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


async def test_unauthenticated_user_cannot_access_owner_only_route(
    test_client: AsyncClient,
) -> None:
    response = await test_client.get("/test/owner-only")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


async def test_owner_can_access_all_roles_route(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user = await make_user(db_session, role=UserRole.OWNER)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await test_client.get(
        "/test/all-roles",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


async def test_admin_can_access_all_roles_route(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user = await make_user(db_session, role=UserRole.ADMIN)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await test_client.get(
        "/test/all-roles",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


async def test_doctor_can_access_all_roles_route(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user = await make_user(db_session, role=UserRole.DOCTOR)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await test_client.get(
        "/test/all-roles",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200


async def test_role_guard_returns_generic_forbidden_message(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    user = await make_user(db_session, role=UserRole.ADMIN)

    token = create_access_token(
        user_id=user.id,
        role=user.role,
        organization_id=user.organization_id,
    )

    response = await test_client.get(
        "/test/owner-only",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "You do not have permission to perform this action"
    )

    assert "owner" not in response.json()["detail"].lower()
    assert "admin" not in response.json()["detail"].lower()
    assert "doctor" not in response.json()["detail"].lower()


def test_require_roles_rejects_empty_roles() -> None:
    with pytest.raises(ValueError):
        require_roles()


def test_require_roles_rejects_invalid_role_type() -> None:
    with pytest.raises(ValueError):
        require_roles("owner")


async def test_user_can_retrive_own_records(
        test_client: AsyncClient,
        db_session: AsyncSession
) -> None:
    organization = await make_organization(db_session)

    user = await make_user(
        db_session,
        organization=organization,
    )

    token = create_access_token(
        user_id=user.id,
        role= user.role,
        organization_id=user.organization_id,
    )

    response = await test_client.get(
        f"/test/users/{user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == user.id


async def test_user_cannot_access_organization_record(
        test_client: AsyncClient,
        db_session: AsyncSession,
) -> None:
    organization_1 = await make_organization(db_session)
    organization_2 = await make_organization(db_session)

    user_1 = await make_user(
        db_session,
        organization=organization_1,
    )

    user_2 = await make_user(
        db_session,
        organization=organization_2
    )

    token = create_access_token(
        user_id=user_1.id,
        role=user_1.role,
        organization_id=user_1.organization_id,
    )

    response = await test_client.get(
        f"/test/users/{user_2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Resource not found"


async def test_cross_organization_and_nonexistent_records_return_same_response(
    test_client: AsyncClient,
    db_session: AsyncSession,
) -> None:
    organization_1 = await make_organization(db_session)
    organization_2 = await make_organization(db_session)

    user_1 = await make_user(
        db_session,
        organization=organization_1,
    )

    user_2 = await make_user(
        db_session,
        organization=organization_2,
    )

    token = create_access_token(
        user_id=user_1.id,
        role=user_1.role,
        organization_id=user_1.organization_id,
    )

    headers = {"Authorization": f"Bearer {token}"}

    cross_org_response = await test_client.get(
        f"/test/users/{user_2.id}",
        headers=headers,
    )

    nonexistent_response = await test_client.get(
        f"/test/users/{user_2.id + 100000}",
        headers=headers,
    )

    assert cross_org_response.status_code == 404
    assert nonexistent_response.status_code == 404

    assert cross_org_response.json() == nonexistent_response.json()


async def test_scoped_lookup_rejects_model_without_organization_id(
    db_session: AsyncSession,
) -> None:
    organization = await make_organization(db_session)

    with pytest.raises(ValueError):
        await get_organization_scoped(
            session=db_session,
            model=Organization,
            object_id=organization.id,
            organization_id=organization.id,
        )


@pytest.fixture
async def test_client(
    db_session: AsyncSession,
) -> AsyncIterator[AsyncClient]:

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        yield db_session

    test_app = FastAPI()

    @test_app.get("/test/owner-only")
    async def owner_only(
        current_user: User = Depends(
            require_roles(UserRole.OWNER)
        ),
    ) -> dict[str, str]:
        return {"message": "owner access granted"}

    @test_app.get("/test/all-roles")
    async def all_roles(
        current_user: User = Depends(
            require_roles(
                UserRole.OWNER,
                UserRole.ADMIN,
                UserRole.DOCTOR,
            )
        ),
    ) -> dict[str, str]:
        return {"message": "Access granted"}
    
    
    @test_app.get("/test/users/{user_id}")
    async def get_user(
        user_id: int,
        current_user: User = Depends(get_current_user),
        session: AsyncSession = Depends(get_db),
    ) -> dict[str, int]:

        user = await get_organization_scoped(
            session=session,
            model=User,
            object_id=user_id,
            organization_id=current_user.organization_id,
        )

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="Resource not found",
            )

        return {"id": user.id}
        

    test_app.dependency_overrides[get_db] = override_get_db

    try:
        async with AsyncClient(
            transport=ASGITransport(app=test_app),
            base_url="http://test",
        ) as client:
            yield client
    finally:
        test_app.dependency_overrides.clear()
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EmailAlreadyRegisteredError
from app.db.session import get_db
from app.schemas.registration import (
    OrganizationRegistrationRequest,
    RegistrationResponse,
)
from app.services.registration_service import register_organization

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.auth import CurrentUserResponse

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

@router.get(
    "/me",
    response_model=CurrentUserResponse,
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> User:
    return current_user


@router.post(
    "/register",
    response_model=RegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    data: OrganizationRegistrationRequest,
    session: AsyncSession = Depends(get_db),
) -> RegistrationResponse:

    try:
        organization, owner = await register_organization(
            session=session,
            data=data,
        )

    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from exc

    return RegistrationResponse(
        organization=organization,
        owner=owner,
    )
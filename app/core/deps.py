
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from collections.abc import Awaitable, Callable

from app.core.tokens import TokenError, decode_access_token
from app.db.session import get_db
from app.models.user import User, UserRole


bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    session: AsyncSession = Depends(get_db),
) -> User:
    unauthorized_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if credentials is None:
        raise unauthorized_exception


    try:
        token_payload = decode_access_token(credentials.credentials)
    except TokenError:
        raise unauthorized_exception from None

   
    user = await session.get(User, token_payload.user_id)

    if user is None:
        raise unauthorized_exception


    if (
            user.role != token_payload.role
            or user.organization_id != token_payload.organization_id
        ):
            raise unauthorized_exception


    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled",
        )

    return user


def require_roles(
        *allowed_roles: UserRole
    ) -> Callable[...,Awaitable[User]]:
    if not allowed_roles:
        raise ValueError("No roles are there, atleast one role must be provided")

    for role in allowed_roles:
        if not isinstance(role, UserRole):
            raise ValueError(f"Invalid Role: {role}")
        

    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
    
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
    
        return current_user

    return role_checker
    
        
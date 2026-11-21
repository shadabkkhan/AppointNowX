from fastapi import APIRouter, Depends

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
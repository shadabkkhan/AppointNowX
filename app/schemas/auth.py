from pydantic import BaseModel, ConfigDict

from app.models.user import UserRole

class CurrentUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: UserRole
    organization_id: int
    is_active: bool
    phone: str | None
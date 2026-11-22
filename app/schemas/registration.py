
import re
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
)

from app.models.organization import OrganizationType


class OrganizationRegistrationRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=False,
    )

    organization_name: str = Field(min_length=2, max_length=150)
    organization_type: OrganizationType
    timezone: str = Field(min_length=1, max_length=50)

    owner_email: EmailStr
    owner_password: SecretStr
    owner_phone: str | None = Field(default=None, max_length=20)

    @field_validator("organization_name", mode="before")
    @classmethod
    def normalize_organization_name(cls, value: object) -> object:
        if isinstance(value, str):
            return " ".join(value.split())
        return value

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Invalid timezone.") from None

        return value

    @field_validator("owner_email", mode="before")
    @classmethod
    def normalize_owner_email(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("owner_password")
    @classmethod
    def validate_owner_password(cls, value: SecretStr) -> SecretStr:
        password = value.get_secret_value()

        if not password.strip():
            raise ValueError("Password cannot be empty or whitespace.")

        if len(password) < 8:
            raise ValueError("Password must contain at least 8 characters.")

        if len(password.encode("utf-8")) > 72:
            raise ValueError("Password cannot exceed 72 UTF-8 bytes.")

        return value

    @field_validator("owner_phone", mode="before")
    @classmethod
    def normalize_owner_phone(cls, value: object) -> object:
        if value is None:
            return None

        if not isinstance(value, str):
            return value

        normalized = re.sub(r"[\s()\-]", "", value)

        if not re.fullmatch(r"\+?[0-9]{7,15}", normalized):
            raise ValueError("Invalid phone number.")

        return normalized

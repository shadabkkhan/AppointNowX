import jwt

from app.models.user import UserRole
from app.core.config import settings

from datetime import datetime, timedelta, timezone

from dataclasses import dataclass
from uuid import uuid4


class TokenError(Exception):
    """will raise when token is invald ror cannot be decoded"""




@dataclass(frozen=True)
class TokenPayload:
    user_id: int
    role: UserRole
    organization_id: int
    jti: str


def create_access_token(
        user_id: int,
        role: UserRole,
        organization_id: int,
        expires_delta: timedelta | None = None
        ) -> str:
    
    issued_at = datetime.now(timezone.utc)

    expires_at = issued_at + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    payload = {
        "sub": str(user_id),
        "role": role.value,
        "organization_id": organization_id,
        "iat": issued_at,
        "exp": expires_at,
        "jti": str(uuid4()),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )

def decode_access_token(token: str) -> TokenPayload:
    if not isinstance(token, str) or not token:
        raise TokenError("Invalid access token")

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
            options={
                "require": [
                    "exp",
                    "iat",
                    "sub",
                    "jti",
                    "role",
                    "organization_id",
                ],
            },
        )

        user_id = int(payload["sub"])
        role = UserRole(payload["role"])
        organization_id = payload["organization_id"]
        jti = payload["jti"]

        if (
            user_id <= 0
            or isinstance(organization_id, bool)
            or not isinstance(organization_id, int)
            or organization_id <= 0
            or not isinstance(jti, str)
            or not jti.strip()
        ):
            raise TokenError("Invalid access token claims.")

        return TokenPayload(
            user_id=user_id,
            role=role,
            organization_id=organization_id,
            jti=jti,
        )

    except TokenError:
        raise

    except (
        jwt.PyJWTError,
        KeyError,
        TypeError,
        ValueError,
        OverflowError,
    ) as exc:
        raise TokenError("Invalid or expired access token.") from exc
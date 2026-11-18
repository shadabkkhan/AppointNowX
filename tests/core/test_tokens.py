
from datetime import timedelta, datetime, timezone

import jwt
import pytest

from app.core.config import settings
from app.core.tokens import (
    TokenError,
    create_access_token,
    decode_access_token,
)
from app.models.user import UserRole


def test_create_access_token_returns_three_part_string():
    token = create_access_token(
        user_id=1,
        role=UserRole.OWNER,
        organization_id=10,
    )

    assert isinstance(token, str)
    assert len(token.split(".")) == 3


def test_decode_access_token_returns_correct_user_details():
    token = create_access_token(
        user_id=5,
        role=UserRole.ADMIN,
        organization_id=20,
    )

    payload = decode_access_token(token)

    assert payload.user_id == 5
    assert payload.role == UserRole.ADMIN
    assert payload.organization_id == 20


def test_token_contains_required_claims_and_correct_expiry():
    token = create_access_token(
        user_id=1,
        role=UserRole.OWNER,
        organization_id=10,
    )

    decoded = jwt.decode(
        token,
        settings.jwt_secret_key.get_secret_value(),
        algorithms=["HS256"],
    )

    assert "iat" in decoded
    assert "exp" in decoded
    assert "jti" in decoded

    assert decoded["exp"] - decoded["iat"] == (
        settings.access_token_expire_minutes * 60
    )


def test_two_tokens_for_same_user_have_different_jti():
    token_one = create_access_token(
        user_id=1,
        role=UserRole.OWNER,
        organization_id=10,
    )

    token_two = create_access_token(
        user_id=1,
        role=UserRole.OWNER,
        organization_id=10,
    )

    payload_one = decode_access_token(token_one)
    payload_two = decode_access_token(token_two)

    assert payload_one.jti != payload_two.jti


def test_expired_token_is_rejected():
    token = create_access_token(
        user_id=1,
        role=UserRole.OWNER,
        organization_id=10,
        expires_delta=timedelta(minutes=-1),
    )

    with pytest.raises(TokenError):
        decode_access_token(token)


def test_modified_token_signature_is_rejected():
    token = create_access_token(
        user_id=1,
        role=UserRole.OWNER,
        organization_id=10,
    )

    header, payload, signature = token.split(".")

    replacement = "A" if signature[0] != "A" else "B"
    tampered_token = ".".join(
        [header, payload, replacement + signature[1:]]
    )

    with pytest.raises(TokenError):
        decode_access_token(tampered_token)


def test_token_signed_with_different_secret_is_rejected():
    token = jwt.encode(
        {
            "sub": "1",
            "role": UserRole.OWNER.value,
            "organization_id": 10,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
            "jti": "test-token-id",
        },
        "a-different-secret-key-that-is-long-enough-123",
        algorithm="HS256",
    )

    with pytest.raises(TokenError):
        decode_access_token(token)


def test_algorithm_none_is_rejected():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "1",
            "role": UserRole.OWNER.value,
            "organization_id": 10,
            "iat": now,
            "exp": now + timedelta(minutes=30),
            "jti": "test-token-id",
        },
        key=None,
        algorithm="none",
    )

    with pytest.raises(TokenError):
        decode_access_token(token)


@pytest.mark.parametrize(
    "missing_claim",
    [
        "sub",
        "exp",
        "jti",
        "role",
        "organization_id",
    ],
)
def test_missing_required_claim_is_rejected(missing_claim):
    now = datetime.now(timezone.utc)

    claims = {
        "sub": "1",
        "role": UserRole.OWNER.value,
        "organization_id": 10,
        "iat": now,
        "exp": now + timedelta(minutes=30),
        "jti": "test-token-id",
    }

    claims.pop(missing_claim)

    token = jwt.encode(
        claims,
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )

    with pytest.raises(TokenError):
        decode_access_token(token)


@pytest.mark.parametrize(
    "invalid_token",
    [
        "",
        "this-is-not-a-jwt",
    ],
)
def test_invalid_token_strings_are_rejected(invalid_token):
    with pytest.raises(TokenError):
        decode_access_token(invalid_token)


def test_token_with_unknown_role_is_rejected():
    now = datetime.now(timezone.utc)

    token = jwt.encode(
        {
            "sub": "1",
            "role": "user",
            "organization_id": 10,
            "iat": now,
            "exp": now + timedelta(minutes=30),
            "jti": "test-token-id",
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )

    with pytest.raises(TokenError):
        decode_access_token(token)

from app.core.security import hash_password, verify_password

import pytest

def test_hash_password_return_bcrypt_hash():
    plain_password = "Dental@123"

    hashed_password = hash_password(plain_password)

    assert hashed_password != plain_password
    assert hashed_password.startswith("$2b$12$")


def test_verify_password_accepts_correct_password():
    plain_password = "Dental@123"

    hashed_password = hash_password(plain_password)

    result = verify_password(plain_password, hashed_password)

    assert result is True


def test_verify_password_rejects_wrong_password():
    plain_password = "Dental@123"
    wrong_password = "Dental#123"

    hashed_password = hash_password(plain_password)

    result = verify_password(wrong_password, hashed_password)

    assert result is False


def test_both_hash_password_verify():
    pass1 = "Dental@123"
    pass2 = "Dental@123"

    hash_pass1 = hash_password(pass1)
    hash_pass2 = hash_password(pass2)

    assert hash_pass1 != hash_pass2
    assert verify_password(pass1, hash_pass1) is True
    assert verify_password(pass2, hash_pass2) is True

def verify_emoji_or_acsent_password():
    password = "Dental🦷123"

    hashed_password = hash_password(password)

    assert isinstance(hashed_password, str)
    assert verify_password(password, hashed_password) is True


def test_hash_password_rejects_more_than_72_ascii_bytes():
    password = "a" * 74

    with pytest.raises(ValueError):
        hash_password(password)

def test_hash_password_rejects_more_than_72_bytes():
    password = "é" * 40

    assert len(password) < 72
    assert len(password.encode("utf-8")) > 72

    with pytest.raises(ValueError):
        hash_password(password)


def test_hash_password_accepts_exactly_72_bytes():
    password = "a" * 72

    hashed_password = hash_password(password)

    assert isinstance(hashed_password, str)
    assert verify_password(password, hashed_password) is True


def test_hash_password_rejects_empty_pass():
    password = ""

    with pytest.raises(ValueError):
        hash_password(password)

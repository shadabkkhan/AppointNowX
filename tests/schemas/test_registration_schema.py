
import pytest

from pydantic import ValidationError, SecretStr

from app.schemas.registration import OrganizationRegistrationRequest
from app.models.organization import OrganizationType


def valid_registration_data() -> dict:
    return {
        "organization_name": "Smile Dental Clinic",
        "organization_type": OrganizationType.CLINIC,
        "timezone": "Asia/Kolkata",
        "owner_email": "owner@example.com",
        "owner_password": "SecurePass123!",
    }


def test_organization_name_is_trimmed_and_normalized():
    data = valid_registration_data()
    data["organization_name"] = "  Smile    Dental    Clinic   "

    registration = OrganizationRegistrationRequest(**data)

    assert registration.organization_name == "Smile Dental Clinic"


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        "a",
        "   a   ",
    ],
)
def test_organization_name_rejects_less_than_two_characters(name):
    data = valid_registration_data()
    data["organization_name"] = name

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)


def test_organization_name_rejects_more_than_150_characters():
    data = valid_registration_data()
    data["organization_name"] = "A" * 151

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)


def test_organization_name_accepts_150_characters():
    data = valid_registration_data()
    data["organization_name"] = "A" * 150

    registration = OrganizationRegistrationRequest(**data)

    assert len(registration.organization_name) == 150


@pytest.mark.parametrize(
    "organization_type",
    [
        OrganizationType.CLINIC,
        OrganizationType.HOSPITAL,
    ],
)
def test_organization_type_accepts_valid_values(organization_type):
    data = valid_registration_data()
    data["organization_type"] = organization_type

    registration = OrganizationRegistrationRequest(**data)

    assert registration.organization_type == organization_type


@pytest.mark.parametrize(
    "organization_type",
    [
        "pharmacy",
        "laboratory",
        "invalid",
        "",
    ],
)
def test_organization_type_rejects_invalid_values(organization_type):
    data = valid_registration_data()
    data["organization_type"] = organization_type

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)



@pytest.mark.parametrize(
    "timezone",
    [
        "Asia/Kolkata",
        "UTC",
    ],
)
def test_timezone_accepts_valid_values(timezone):
    data = valid_registration_data()
    data["timezone"] = timezone

    registration = OrganizationRegistrationRequest(**data)

    assert registration.timezone == timezone


@pytest.mark.parametrize(
    "timezone",
    [
        "Mars/Olympus",
        "",
        " ",
        "Invalid",
    ],
)
def test_timezone_rejects_invalid_values(timezone):
    data = valid_registration_data()
    data["timezone"] = timezone

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)


def test_owner_email_is_trimmed_and_lowercased():
    data = valid_registration_data()
    data["owner_email"] = " Owner@Example.COM "

    registration = OrganizationRegistrationRequest(**data)

    assert registration.owner_email == "owner@example.com"


@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",
        "owner@",
        "@example.com",
        "",
        " ",
    ],
)
def test_owner_email_rejects_invalid_values(email):
    data = valid_registration_data()
    data["owner_email"] = email

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)


def test_owner_password_accepts_eight_characters():
    data = valid_registration_data()
    data["owner_password"] = "Abc12345"

    registration = OrganizationRegistrationRequest(**data)

    assert registration.owner_password.get_secret_value() == "Abc12345"


@pytest.mark.parametrize(
    "password",
    [
        "Abc1234",
        "",
        "        ",
    ],
)
def test_owner_password_rejects_invalid_values(password):
    data = valid_registration_data()
    data["owner_password"] = password

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)


def test_owner_password_rejects_more_than_72_utf8_bytes():
    data = valid_registration_data()
    data["owner_password"] = "A" * 73

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)


def test_owner_password_rejects_multibyte_password_over_72_bytes():
    data = valid_registration_data()
    data["owner_password"] = "é" * 37

    assert len(data["owner_password"]) == 37
    assert len(data["owner_password"].encode("utf-8")) == 74

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)


def test_owner_password_uses_secret_str():
    data = valid_registration_data()

    registration = OrganizationRegistrationRequest(**data)

    assert isinstance(registration.owner_password, SecretStr)


def test_owner_password_is_not_exposed_in_string_representation():
    data = valid_registration_data()
    registration = OrganizationRegistrationRequest(**data)

    assert data["owner_password"] not in str(registration)
    assert data["owner_password"] not in repr(registration)


def test_owner_phone_is_optional():
    data = valid_registration_data()

    registration = OrganizationRegistrationRequest(**data)

    assert registration.owner_phone is None


@pytest.mark.parametrize(
    "phone",
    [
        "+91 98765-43210",
        "+91 (98765) 43210",
    ],
)
def test_owner_phone_is_normalized(phone):
    data = valid_registration_data()
    data["owner_phone"] = phone

    registration = OrganizationRegistrationRequest(**data)

    assert registration.owner_phone == "+919876543210"


@pytest.mark.parametrize(
    "phone",
    [
        "abc",
        "98765abc",
        "",
        " ",
        "+91-",
    ],
)
def test_owner_phone_rejects_invalid_values(phone):
    data = valid_registration_data()
    data["owner_phone"] = phone

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)


@pytest.mark.parametrize(
    "extra_field",
    [
        "role",
        "organization_id",
        "is_verified",
        "is_active",
    ],
)
def test_registration_rejects_extra_fields(extra_field):
    data = valid_registration_data()
    data[extra_field] = "unexpected-value"

    with pytest.raises(ValidationError):
        OrganizationRegistrationRequest(**data)

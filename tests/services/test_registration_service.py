import pytest

from sqlalchemy import func, select

from app.core.exceptions import EmailAlreadyRegisteredError
from app.core.security import verify_password
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.registration import OrganizationRegistrationRequest
from app.services.registration_service import register_organization

def valid_registration_data(**overrides):
    data = {
        "organization_name": "Smile Dental Clinic",
        "organization_type": "clinic",
        "timezone": "Asia/Kolkata",
        "owner_email": "owner@example.com",
        "owner_password": "SecurePass123!",
        "owner_phone": "+919876543210",
    }

    data.update(overrides)

    return OrganizationRegistrationRequest(**data)


async def test_register_organization_creates_organization_and_owner(db_session):
    data = valid_registration_data()

    organization, owner = await register_organization(db_session, data)

    assert organization.id is not None
    assert organization.name == "Smile Dental Clinic"
    assert organization.type.value == "clinic"
    assert organization.timezone == "Asia/Kolkata"

    assert owner.id is not None
    assert owner.email == "owner@example.com"
    assert owner.role == UserRole.OWNER
    assert owner.organization_id == organization.id
    assert owner.is_active is True
    assert owner.is_verified is False
    assert owner.phone == "+919876543210"

    assert owner.hash_password.startswith("$2b$")
    assert verify_password(
        "SecurePass123!",
        owner.hash_password,
    )
    assert "SecurePass123!" not in owner.hash_password


async def test_register_organization_rejects_duplicate_email(db_session):
    first_data = valid_registration_data()

    await register_organization(db_session, first_data)

    duplicate_data = valid_registration_data(
        organization_name="Another Dental Clinic",
    )

    with pytest.raises(EmailAlreadyRegisteredError):
        await register_organization(db_session, duplicate_data)


async def test_duplicate_email_does_not_create_orphan_organization(db_session):
    await register_organization(
        db_session,
        valid_registration_data(),
    )

    organization_count_before = await db_session.scalar(
        select(func.count()).select_from(Organization)
    )

    with pytest.raises(EmailAlreadyRegisteredError):
        await register_organization(
            db_session,
            valid_registration_data(
                organization_name="Second Dental Clinic",
            ),
        )

    organization_count_after = await db_session.scalar(
        select(func.count()).select_from(Organization)
    )

    assert organization_count_after == organization_count_before


async def test_session_remains_usable_after_duplicate_email(db_session):
    await register_organization(
        db_session,
        valid_registration_data(),
    )

    with pytest.raises(EmailAlreadyRegisteredError):
        await register_organization(
            db_session,
            valid_registration_data(),
        )

    organization, owner = await register_organization(
        db_session,
        valid_registration_data(
            organization_name="Third Dental Clinic",
            owner_email="third@example.com",
        ),
    )

    assert organization.id is not None
    assert owner.email == "third@example.com"

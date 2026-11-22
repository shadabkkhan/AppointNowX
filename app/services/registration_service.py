
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import EmailAlreadyRegisteredError
from app.core.security import hash_password
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.schemas.registration import OrganizationRegistrationRequest


async def register_organization(
    session: AsyncSession,
    data: OrganizationRegistrationRequest,
) -> tuple[Organization, User]:
    try:
        organization = Organization(
            name=data.organization_name,
            type=data.organization_type,
            timezone=data.timezone,
        )

        session.add(organization)
        await session.flush()

        owner = User(
            email=str(data.owner_email),
            hash_password=hash_password(
                data.owner_password.get_secret_value()
            ),
            phone=data.owner_phone,
            role=UserRole.OWNER,
            is_active=True,
            is_verified=False,
            organization_id=organization.id,
        )

        session.add(owner)
        await session.flush()

        await session.commit()

        return organization, owner

    except IntegrityError as exc:
        await session.rollback()

        original_error = exc.orig
        error_code = getattr(original_error, "args", (None,))[0]

        error_message = str(original_error).lower()

        print("MYSQL ERROR CODE:", error_code)
        print("MYSQL ERROR MESSAGE:", repr(error_message))

        if (
            error_code == 1062
            and "for key 'users.email'" in error_message
        ):
            raise EmailAlreadyRegisteredError(
                "An account with this email already exists."
            ) from exc

        raise

    except Exception:
        await session.rollback()
        raise

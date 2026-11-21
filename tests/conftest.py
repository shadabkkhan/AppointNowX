import os
import sys
from pathlib import Path
import subprocess
import pytest

from dotenv import dotenv_values
from sqlalchemy.engine import make_url

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = PROJECT_ROOT / ".env"

file_environment = dotenv_values(ENV_FILE)

test_database_url = (
    os.environ.get("TEST_DATABASE_URL")
    or file_environment.get("TEST_DATABASE_URL")
)

development_database_url = (
    os.environ.get("DATABASE_URL")
    or file_environment.get("DATABASE_URL")
)

if not test_database_url:
    raise RuntimeError("TEST_DB_URL is not configured")

if not development_database_url:
    raise RuntimeError("DB_URL is not configured.")

try:
    test_url = make_url(test_database_url)
    development_database_url = make_url(development_database_url)
except Exception as exc:
    raise RuntimeError("DB url is invalid") from exc

if not test_url.database or not test_url.database.endswith("_test"):
    raise RuntimeError("Tets db name must ends with '_test'")

if test_url.database == development_database_url.database:
    raise RuntimeError("Tets db and developemnt db must be different ")

if test_url.host not in {"localhost", "127.0.0.1"}:
    raise RuntimeError("Test db must use localhost or 127.0.0.1")

os.environ["DATABASE_URL"] = test_database_url

os.environ["JWT_SECRET_KEY"] = (
    "testonly_secret_key-for-appointments-123445555@#"
)

os.environ["JWT_ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"

@pytest.fixture(scope="session")
def migrated_database() -> None:
    environment = os.environ.copy()
    environment["DATABASE_URL"] = test_database_url

    commands = [
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        [sys.executable, "-m", "alembic", "check"],
    ]

    for command in commands:
        result = subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Alembic command failed: {' '.join(command)}\n"
                f"STDOUT:\n{result.stdout}\n"
                f"STDERR:\n{result.stderr}"
            )

@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def db_session(
    migrated_database: None,
) -> AsyncIterator[AsyncSession]:
    from app.core.config import settings

    if not settings.database_url:
        raise RuntimeError("Db URL is not configured.")

    engine = create_async_engine(
        settings.database_url,
        poolclass=NullPool,
    )

    try:
        async with engine.connect() as connection:
            outer_transaction = await connection.begin()

            session = AsyncSession(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint",
            )

            try:
                yield session
            finally:
                try:
                    await session.close()
                finally:
                    if outer_transaction.is_active:
                        await outer_transaction.rollback()

    finally:
        await engine.dispose()
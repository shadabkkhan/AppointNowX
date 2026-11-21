from app.core.config import settings
from sqlalchemy.engine import make_url

from sqlalchemy import create_engine, inspect

def test_settings_use_test_database(migrated_database):
    database_url = make_url(settings.database_url)

    assert database_url.database.endswith("_test")


def test_required_tables_exist(migrated_database):
    database_url = make_url(settings.database_url)

    sync_database_url = database_url.set(
        drivername="mysql+pymysql"
    )

    engine = create_engine(sync_database_url)

    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            tables = set(inspector.get_table_names())

        expected_tables = {
            "organizations",
            "users",
            "doctors",
            "appointments",
            "ai_conversations",
            "alembic_version",
        }

        assert expected_tables.issubset(tables)

    finally:
        engine.dispose()
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


APPLICATION_TABLES = {
    "allocations",
    "assets",
    "optimization_runs",
    "portfolio_briefs",
    "price_readings",
}


def test_empty_database_upgrade_downgrade_upgrade(
    tmp_path: Path, monkeypatch
) -> None:
    database_path = tmp_path / "migration-round-trip.db"
    database_url = f"sqlite+pysqlite:///{database_path}"
    monkeypatch.setenv("DATABASE_URL", database_url)
    alembic_config = Config("alembic.ini")
    engine = create_engine(database_url)

    command.upgrade(alembic_config, "head")
    assert APPLICATION_TABLES <= set(inspect(engine).get_table_names())
    assert _current_revision(engine) == "20260819_0002"

    command.downgrade(alembic_config, "base")
    assert APPLICATION_TABLES.isdisjoint(inspect(engine).get_table_names())

    command.upgrade(alembic_config, "head")
    assert APPLICATION_TABLES <= set(inspect(engine).get_table_names())
    assert _current_revision(engine) == "20260819_0002"

    engine.dispose()


def _current_revision(engine) -> str:
    with engine.connect() as connection:
        return connection.exec_driver_sql(
            "SELECT version_num FROM alembic_version"
        ).scalar_one()

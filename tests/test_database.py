from portfolio_optimization.config import DatabaseConfig
from portfolio_optimization.database import create_database_engine, ping_database


def test_database_ping_executes_query() -> None:
    config = DatabaseConfig(
        database_url="sqlite+pysqlite:///:memory:",
    )
    engine = create_database_engine(config)

    assert ping_database(engine) is True

    engine.dispose()

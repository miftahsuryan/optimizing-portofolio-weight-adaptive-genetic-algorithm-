from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from portfolio_optimization.config import DatabaseConfig, load_database_config


def create_database_engine(config: DatabaseConfig) -> Engine:
    """Create the process-wide SQLAlchemy engine from validated settings."""
    return create_engine(
        config.database_url,
        echo=config.database_echo,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_database_engine(load_database_config())


def get_session() -> Iterator[Session]:
    """Yield one transaction-scoped session for a request or worker job."""
    factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    with factory() as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def ping_database(engine: Engine | None = None) -> bool:
    """Execute a minimal round trip; connection errors remain observable."""
    target = engine or get_engine()
    with target.connect() as connection:
        return connection.execute(text("SELECT 1")).scalar_one() == 1

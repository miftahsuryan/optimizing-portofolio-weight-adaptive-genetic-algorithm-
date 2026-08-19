from collections.abc import Iterator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.dependencies import get_database_session
from apps.api.main import app
from portfolio_optimization.repositories.postgres_briefs import metadata


def test_brief_round_trip_survives_a_fresh_client() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def session_override() -> Iterator[Session]:
        with factory() as session:
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise

    app.dependency_overrides[get_database_session] = session_override
    try:
        with TestClient(app) as first_client:
            response = first_client.post(
                "/briefs",
                json={"name": "Retirement 2045", "risk_profile": "balanced"},
            )
        assert response.status_code == 201
        created = response.json()
        assert created["name"] == "Retirement 2045"
        assert created["ai_summary"] == (
            "AI stub: balance growth and stability with 50% broad-market "
            "equity, 40% bonds, and 10% cash."
        )

        # A new HTTP client models a fresh UI/API run while reusing persisted DB.
        with TestClient(app) as fresh_client:
            listed = fresh_client.get("/briefs")
        assert listed.status_code == 200
        assert listed.json() == [created]
    finally:
        app.dependency_overrides.clear()
        engine.dispose()


def test_ai_stub_is_deterministic_for_the_same_risk_profile() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    metadata.create_all(engine)
    with Session(engine) as session:
        from portfolio_optimization.repositories.postgres_briefs import (
            PostgresPortfolioBriefRepository,
        )
        from portfolio_optimization.services.brief_service import (
            PortfolioBriefService,
        )
        from portfolio_optimization.domain import RiskProfile

        service = PortfolioBriefService(PostgresPortfolioBriefRepository(session))
        first = service.create(name="One", risk_profile=RiskProfile.GROWTH)
        second = service.create(name="Two", risk_profile=RiskProfile.GROWTH)

    assert first.ai_summary == second.ai_summary

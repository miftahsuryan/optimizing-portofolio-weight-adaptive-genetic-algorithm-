"""Integration coverage for API dependency injection and SQL repositories."""

from collections.abc import Iterator
from datetime import datetime
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from apps.api.dependencies import get_database_session
from apps.api.main import app
from portfolio_optimization.repositories.models import Base


def test_asset_api_reads_rows_written_by_an_earlier_request() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
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
        with TestClient(app) as writer:
            created_response = writer.post(
                "/assets",
                json={
                    "symbol": "bbca",
                    "name": "Bank Central Asia",
                    "currency": "idr",
                },
            )
        assert created_response.status_code == 201
        created = created_response.json()

        with TestClient(app) as writer:
            reading_response = writer.post(
                f"/assets/{created['id']}/readings",
                json={
                    "observed_at": "2026-08-20T02:00:00Z",
                    "close": "8500.50",
                },
            )
        assert reading_response.status_code == 201
        reading = reading_response.json()

        # A separate request/client proves state belongs to SQL, not a fake.
        with TestClient(app) as reader:
            listed_response = reader.get("/assets")
            fetched_response = reader.get(f"/assets/{created['id']}")
            readings_response = reader.get(
                f"/assets/{created['id']}/readings"
            )

        assert listed_response.status_code == 200
        assert listed_response.json() == [created]
        assert fetched_response.status_code == 200
        assert fetched_response.json() == created
        assert readings_response.status_code == 200
        persisted_reading = readings_response.json()[0]
        assert persisted_reading["id"] == reading["id"]
        assert persisted_reading["asset_id"] == created["id"]
        assert Decimal(persisted_reading["close"]) == Decimal("8500.50")
        assert datetime.fromisoformat(
            persisted_reading["observed_at"].replace("Z", "+00:00")
        ) == datetime.fromisoformat(reading["observed_at"])
    finally:
        app.dependency_overrides.clear()
        engine.dispose()

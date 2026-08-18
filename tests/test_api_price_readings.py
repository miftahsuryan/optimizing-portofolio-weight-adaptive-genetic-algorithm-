from collections.abc import Iterator
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from apps.api.dependencies import (
    get_asset_service,
    get_price_reading_service,
)
from apps.api.main import app
from portfolio_optimization.repositories.in_memory import (
    InMemoryAssetRepository,
    InMemoryPriceReadingRepository,
)
from portfolio_optimization.services.asset_service import AssetService
from portfolio_optimization.services.price_reading_service import (
    PriceReadingService,
)


@pytest.fixture
def client() -> Iterator[TestClient]:
    asset_repository = InMemoryAssetRepository()
    reading_repository = InMemoryPriceReadingRepository()

    asset_service = AssetService(
        repository=asset_repository,
    )
    reading_service = PriceReadingService(
        asset_repository=asset_repository,
        reading_repository=reading_repository,
    )

    app.dependency_overrides[get_asset_service] = (
        lambda: asset_service
    )
    app.dependency_overrides[get_price_reading_service] = (
        lambda: reading_service
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def create_asset(client: TestClient) -> dict[str, Any]:
    response = client.post(
        "/assets",
        json={
            "symbol": "BBCA",
            "name": "Bank Central Asia",
            "currency": "IDR",
        },
    )

    assert response.status_code == 201
    return response.json()


def create_reading(
    client: TestClient,
    asset_id: str,
    *,
    observed_at: str = "2026-08-17T09:00:00+00:00",
    close: str = "8500.50",
) -> dict[str, Any]:
    response = client.post(
        f"/assets/{asset_id}/readings",
        json={
            "observed_at": observed_at,
            "close": close,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_reading_for_asset(client: TestClient) -> None:
    asset = create_asset(client)

    reading = create_reading(client, asset["id"])

    assert reading["asset_id"] == asset["id"]
    assert reading["observed_at"] == "2026-08-17T09:00:00Z"
    assert reading["close"] == "8500.50"
    assert "id" in reading
    assert "created_at" in reading


def test_create_reading_returns_404_for_unknown_asset(
    client: TestClient,
) -> None:
    unknown_asset_id = uuid4()

    response = client.post(
        f"/assets/{unknown_asset_id}/readings",
        json={
            "observed_at": "2026-08-17T09:00:00Z",
            "close": "8500",
        },
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "entity_not_found"


def test_create_reading_returns_409_for_duplicate_observation(
    client: TestClient,
) -> None:
    asset = create_asset(client)
    create_reading(client, asset["id"])

    response = client.post(
        f"/assets/{asset['id']}/readings",
        json={
            "observed_at": "2026-08-17T09:00:00Z",
            "close": "8600",
        },
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "duplicate_entity"


def test_create_reading_returns_422_for_invalid_close(
    client: TestClient,
) -> None:
    asset = create_asset(client)

    response = client.post(
        f"/assets/{asset['id']}/readings",
        json={
            "observed_at": "2026-08-17T09:00:00Z",
            "close": "0",
        },
    )

    assert response.status_code == 422


def test_list_readings_returns_chronological_data(
    client: TestClient,
) -> None:
    asset = create_asset(client)
    later = create_reading(
        client,
        asset["id"],
        observed_at="2026-08-18T09:00:00Z",
        close="8600",
    )
    earlier = create_reading(
        client,
        asset["id"],
        observed_at="2026-08-17T09:00:00Z",
        close="8500",
    )

    response = client.get(
        f"/assets/{asset['id']}/readings"
    )

    assert response.status_code == 200
    assert response.json() == [earlier, later]


def test_list_readings_applies_time_filter_and_pagination(
    client: TestClient,
) -> None:
    asset = create_asset(client)
    create_reading(
        client,
        asset["id"],
        observed_at="2026-08-16T09:00:00Z",
    )
    expected = create_reading(
        client,
        asset["id"],
        observed_at="2026-08-17T09:00:00Z",
    )
    create_reading(
        client,
        asset["id"],
        observed_at="2026-08-18T09:00:00Z",
    )

    response = client.get(
        f"/assets/{asset['id']}/readings",
        params={
            "observed_from": "2026-08-17T00:00:00Z",
            "observed_to": "2026-08-18T00:00:00Z",
            "offset": 0,
            "limit": 1,
        },
    )

    assert response.status_code == 200
    assert response.json() == [expected]


def test_create_reading_batch(client: TestClient) -> None:
    asset = create_asset(client)

    response = client.post(
        f"/assets/{asset['id']}/readings/batch",
        json={
            "readings": [
                {
                    "observed_at": "2026-08-17T09:00:00Z",
                    "close": "8500",
                },
                {
                    "observed_at": "2026-08-18T09:00:00Z",
                    "close": "8600",
                },
            ]
        },
    )

    assert response.status_code == 201
    assert len(response.json()) == 2


def test_create_reading_batch_rejects_empty_list(
    client: TestClient,
) -> None:
    asset = create_asset(client)

    response = client.post(
        f"/assets/{asset['id']}/readings/batch",
        json={"readings": []},
    )

    assert response.status_code == 422


def test_get_reading_returns_existing_reading(
    client: TestClient,
) -> None:
    asset = create_asset(client)
    reading = create_reading(client, asset["id"])

    response = client.get(f"/readings/{reading['id']}")

    assert response.status_code == 200
    assert response.json() == reading


def test_delete_reading(client: TestClient) -> None:
    asset = create_asset(client)
    reading = create_reading(client, asset["id"])

    response = client.delete(f"/readings/{reading['id']}")

    assert response.status_code == 204
    assert response.content == b""

    get_response = client.get(f"/readings/{reading['id']}")
    assert get_response.status_code == 404

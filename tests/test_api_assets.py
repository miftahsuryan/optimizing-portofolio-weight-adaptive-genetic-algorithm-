from collections.abc import Iterator
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from apps.api.dependencies import get_asset_service
from apps.api.main import app
from portfolio_optimization.repositories.in_memory import (
    InMemoryAssetRepository,
)
from portfolio_optimization.services.asset_service import AssetService


@pytest.fixture
def client() -> Iterator[TestClient]:
    repository = InMemoryAssetRepository()
    service = AssetService(repository=repository)

    app.dependency_overrides[get_asset_service] = lambda: service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def create_asset(
    client: TestClient,
    *,
    symbol: str = "BBCA",
    name: str = "Bank Central Asia",
) -> dict[str, Any]:
    response = client.post(
        "/assets",
        json={
            "symbol": symbol,
            "name": name,
            "currency": "IDR",
        },
    )

    assert response.status_code == 201
    return response.json()


def test_create_asset_returns_created_asset(
    client: TestClient,
) -> None:
    body = create_asset(client)

    assert body["symbol"] == "BBCA"
    assert body["name"] == "Bank Central Asia"
    assert body["currency"] == "IDR"
    assert "id" in body
    assert "created_at" in body
    assert body["updated_at"] == body["created_at"]


def test_list_assets_returns_created_assets(
    client: TestClient,
) -> None:
    first = create_asset(client)
    second = create_asset(
        client,
        symbol="BBRI",
        name="Bank Rakyat Indonesia",
    )

    response = client.get("/assets")

    assert response.status_code == 200
    assert response.json() == [first, second]


def test_get_asset_returns_existing_asset(
    client: TestClient,
) -> None:
    created = create_asset(client)

    response = client.get(f"/assets/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_asset_returns_404_for_unknown_id(
    client: TestClient,
) -> None:
    unknown_id = uuid4()

    response = client.get(f"/assets/{unknown_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "entity_not_found",
            "message": f"Asset not found: {unknown_id}",
        }
    }


def test_create_asset_returns_409_for_duplicate_symbol(
    client: TestClient,
) -> None:
    create_asset(client)

    response = client.post(
        "/assets",
        json={
            "symbol": "bbca",
            "name": "Duplicate Asset",
            "currency": "IDR",
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "duplicate_entity",
            "message": "Asset symbol already exists: BBCA",
        }
    }


def test_create_asset_returns_422_for_invalid_request(
    client: TestClient,
) -> None:
    response = client.post(
        "/assets",
        json={
            "symbol": "",
            "name": "Invalid Asset",
            "currency": "INVALID",
        },
    )

    assert response.status_code == 422


def test_update_asset_returns_updated_asset(
    client: TestClient,
) -> None:
    created = create_asset(client)

    response = client.patch(
        f"/assets/{created['id']}",
        json={
            "symbol": "bca",
            "name": "PT Bank Central Asia",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == created["id"]
    assert body["symbol"] == "BCA"
    assert body["name"] == "PT Bank Central Asia"
    assert body["currency"] == "IDR"
    assert body["created_at"] == created["created_at"]


def test_update_asset_returns_422_for_empty_update(
    client: TestClient,
) -> None:
    created = create_asset(client)

    response = client.patch(
        f"/assets/{created['id']}",
        json={},
    )

    assert response.status_code == 422
    assert response.json() == {
        "error": {
            "code": "domain_validation_error",
            "message": "At least one Asset field must be provided",
        }
    }


def test_delete_asset_removes_asset(
    client: TestClient,
) -> None:
    created = create_asset(client)

    delete_response = client.delete(f"/assets/{created['id']}")

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    get_response = client.get(f"/assets/{created['id']}")

    assert get_response.status_code == 404


def test_delete_asset_returns_404_for_unknown_id(
    client: TestClient,
) -> None:
    unknown_id = uuid4()

    response = client.delete(f"/assets/{unknown_id}")

    assert response.status_code == 404
from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from apps.api.dependencies import get_optimization_service
from apps.api.main import app
from portfolio_optimization.domain import Asset, PriceReading
from portfolio_optimization.repositories.in_memory import (
    InMemoryAssetRepository,
    InMemoryOptimizationRepository,
    InMemoryPriceReadingRepository,
)
from portfolio_optimization.services.optimization_service import (
    OptimizationService,
)


@pytest.fixture
def optimization_client() -> Iterator[TestClient]:
    asset_repository = InMemoryAssetRepository()
    reading_repository = InMemoryPriceReadingRepository()
    optimization_repository = InMemoryOptimizationRepository()
    base_time = datetime(2026, 8, 1, tzinfo=UTC)
    price_series = (
        ("AAA", [100, 103, 102, 106]),
        ("BBB", [200, 198, 205, 207]),
        ("CCC", [80, 82, 85, 84]),
        ("DDD", [150, 151, 155, 160]),
    )
    for symbol, prices in price_series:
        asset = asset_repository.create(
            Asset(symbol=symbol, name=f"Asset {symbol}", currency="IDR")
        )
        reading_repository.create_many(
            PriceReading(
                asset_id=asset.id,
                observed_at=base_time + timedelta(days=index),
                close=Decimal(str(price)),
            )
            for index, price in enumerate(prices)
        )

    service = OptimizationService(
        asset_repository=asset_repository,
        reading_repository=reading_repository,
        optimization_repository=optimization_repository,
    )
    app.dependency_overrides[get_optimization_service] = lambda: service
    app.state.optimization_asset_ids = [
        asset.id for asset in asset_repository.list_all()
    ]
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def optimization_request() -> dict[str, object]:
    return {
        "asset_ids": [
            str(asset_id) for asset_id in app.state.optimization_asset_ids
        ],
        "start_date": "2026-08-01",
        "end_date": "2026-08-04",
        "population_size": 20,
        "generations": 10,
        "max_weight": 0.4,
        "seed": 29,
    }


def test_run_get_and_list_sga_optimization(
    optimization_client: TestClient,
) -> None:
    create_response = optimization_client.post(
        "/optimizations/sga",
        json=optimization_request(),
    )

    assert create_response.status_code == 201
    body = create_response.json()
    assert body["method"] == "SGA"
    assert body["status"] == "completed"
    assert len(body["allocations"]) == 4
    total = sum(
        Decimal(allocation["weight"])
        for allocation in body["allocations"]
    )
    assert total == Decimal("1")
    assert all(
        Decimal(allocation["weight"]) <= Decimal("0.4")
        for allocation in body["allocations"]
    )

    get_response = optimization_client.get(
        f"/optimizations/{body['id']}"
    )
    assert get_response.status_code == 200
    assert get_response.json() == body

    list_response = optimization_client.get("/optimizations")
    assert list_response.status_code == 200
    assert list_response.json() == [body]


def test_infeasible_optimization_is_not_persisted(
    optimization_client: TestClient,
) -> None:
    request = optimization_request()
    request["max_weight"] = 0.2

    response = optimization_client.post(
        "/optimizations/sga",
        json=request,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "domain_validation_error"
    assert optimization_client.get("/optimizations").json() == []


def test_get_unknown_optimization_returns_404(
    optimization_client: TestClient,
) -> None:
    response = optimization_client.get(f"/optimizations/{uuid4()}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "entity_not_found"

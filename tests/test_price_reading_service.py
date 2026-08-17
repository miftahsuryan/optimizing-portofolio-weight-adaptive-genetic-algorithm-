from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from portfolio_optimization.domain import Asset
from portfolio_optimization.exceptions import (
    DomainValidationError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from portfolio_optimization.repositories.in_memory import (
    InMemoryAssetRepository,
    InMemoryPriceReadingRepository,
)
from portfolio_optimization.services.price_reading_service import (
    PriceReadingService,
)


OBSERVED_AT = datetime(2026, 8, 17, 9, 0, tzinfo=UTC)
CREATED_AT = datetime(2026, 8, 17, 10, 0, tzinfo=UTC)


def make_service() -> tuple[
    PriceReadingService,
    InMemoryAssetRepository,
    InMemoryPriceReadingRepository,
]:
    asset_repository = InMemoryAssetRepository()
    reading_repository = InMemoryPriceReadingRepository()
    service = PriceReadingService(
        asset_repository=asset_repository,
        reading_repository=reading_repository,
        clock=lambda: CREATED_AT,
    )
    return service, asset_repository, reading_repository


def create_asset(
    repository: InMemoryAssetRepository,
    *,
    symbol: str = "BBCA",
) -> Asset:
    return repository.create(
        Asset(
            symbol=symbol,
            name="Test Asset",
            currency="IDR",
        )
    )


def test_create_reading_for_existing_asset() -> None:
    service, asset_repository, reading_repository = make_service()
    asset = create_asset(asset_repository)

    result = service.create_reading(
        asset_id=asset.id,
        observed_at=OBSERVED_AT,
        close=Decimal("8500.50"),
    )

    assert result.asset_id == asset.id
    assert result.observed_at == OBSERVED_AT
    assert result.close == Decimal("8500.50")
    assert result.created_at == CREATED_AT
    assert reading_repository.get(result.id) == result


def test_create_reading_rejects_unknown_asset() -> None:
    service, _asset_repository, reading_repository = make_service()
    unknown_asset_id = uuid4()

    with pytest.raises(
        EntityNotFoundError,
        match=f"Asset not found: {unknown_asset_id}",
    ):
        service.create_reading(
            asset_id=unknown_asset_id,
            observed_at=OBSERVED_AT,
            close=Decimal("8500.50"),
        )

    assert reading_repository.list_for_asset(unknown_asset_id) == ()


def test_get_reading_returns_existing_reading() -> None:
    service, asset_repository, _reading_repository = make_service()
    asset = create_asset(asset_repository)
    created = service.create_reading(
        asset_id=asset.id,
        observed_at=OBSERVED_AT,
        close=Decimal("8500.50"),
    )

    result = service.get_reading(created.id)

    assert result == created


def test_get_reading_rejects_unknown_reading() -> None:
    service, _asset_repository, _reading_repository = make_service()
    unknown_reading_id = uuid4()

    with pytest.raises(
        EntityNotFoundError,
        match=f"PriceReading not found: {unknown_reading_id}",
    ):
        service.get_reading(unknown_reading_id)


def test_list_readings_returns_chronological_data() -> None:
    service, asset_repository, _reading_repository = make_service()
    asset = create_asset(asset_repository)
    later = service.create_reading(
        asset_id=asset.id,
        observed_at=OBSERVED_AT + timedelta(days=1),
        close=Decimal("8600"),
    )
    earlier = service.create_reading(
        asset_id=asset.id,
        observed_at=OBSERVED_AT,
        close=Decimal("8500"),
    )

    result = service.list_readings(asset.id)

    assert result == (earlier, later)


def test_list_readings_rejects_unknown_asset() -> None:
    service, _asset_repository, _reading_repository = make_service()
    unknown_asset_id = uuid4()

    with pytest.raises(
        EntityNotFoundError,
        match=f"Asset not found: {unknown_asset_id}",
    ):
        service.list_readings(unknown_asset_id)


def test_create_readings_stores_complete_batch() -> None:
    service, asset_repository, reading_repository = make_service()
    asset = create_asset(asset_repository)
    values = (
        (OBSERVED_AT, Decimal("8500")),
        (
            OBSERVED_AT + timedelta(days=1),
            Decimal("8600"),
        ),
    )

    result = service.create_readings(
        asset_id=asset.id,
        values=values,
    )

    assert len(result) == 2
    assert result[0].created_at == CREATED_AT
    assert result[1].created_at == CREATED_AT
    assert reading_repository.list_for_asset(asset.id) == result


def test_create_readings_rejects_empty_batch() -> None:
    service, asset_repository, _reading_repository = make_service()
    asset = create_asset(asset_repository)

    with pytest.raises(
        DomainValidationError,
        match="At least one PriceReading must be provided",
    ):
        service.create_readings(
            asset_id=asset.id,
            values=(),
        )


def test_create_readings_is_atomic_for_duplicate_observation() -> None:
    service, asset_repository, reading_repository = make_service()
    asset = create_asset(asset_repository)
    values = (
        (OBSERVED_AT, Decimal("8500")),
        (OBSERVED_AT, Decimal("8600")),
    )

    with pytest.raises(
        DuplicateEntityError,
        match="PriceReading already exists for Asset",
    ):
        service.create_readings(
            asset_id=asset.id,
            values=values,
        )

    assert reading_repository.list_for_asset(asset.id) == ()


def test_delete_reading_removes_existing_reading() -> None:
    service, asset_repository, reading_repository = make_service()
    asset = create_asset(asset_repository)
    reading = service.create_reading(
        asset_id=asset.id,
        observed_at=OBSERVED_AT,
        close=Decimal("8500"),
    )

    service.delete_reading(reading.id)

    assert reading_repository.get(reading.id) is None


def test_delete_reading_rejects_unknown_reading() -> None:
    service, _asset_repository, _reading_repository = make_service()
    unknown_reading_id = uuid4()

    with pytest.raises(
        EntityNotFoundError,
        match=f"PriceReading not found: {unknown_reading_id}",
    ):
        service.delete_reading(unknown_reading_id)
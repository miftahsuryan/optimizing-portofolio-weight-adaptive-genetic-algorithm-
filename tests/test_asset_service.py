from datetime import UTC, datetime, timedelta
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
)
from portfolio_optimization.services.asset_service import AssetService


CREATED_AT = datetime(2026, 8, 17, 8, 0, tzinfo=UTC)
UPDATED_AT = CREATED_AT + timedelta(hours=1)


def make_service(
    *,
    current_time: datetime = CREATED_AT,
) -> tuple[AssetService, InMemoryAssetRepository]:
    repository = InMemoryAssetRepository()
    service = AssetService(
        repository=repository,
        clock=lambda: current_time,
    )
    return service, repository


def test_create_asset_stores_normalized_asset() -> None:
    service, repository = make_service()

    result = service.create_asset(
        symbol=" bbca ",
        name=" Bank Central Asia ",
        currency=" idr ",
    )

    assert result.symbol == "BBCA"
    assert result.name == "Bank Central Asia"
    assert result.currency == "IDR"
    assert result.created_at == CREATED_AT
    assert result.updated_at == CREATED_AT
    assert repository.get(result.id) == result


def test_create_asset_rejects_duplicate_symbol() -> None:
    service, _repository = make_service()
    service.create_asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
    )

    with pytest.raises(
        DuplicateEntityError,
        match="Asset symbol already exists: BBCA",
    ):
        service.create_asset(
            symbol="bbca",
            name="Another Asset",
            currency="IDR",
        )


def test_get_asset_returns_existing_asset() -> None:
    service, _repository = make_service()
    created = service.create_asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
    )

    result = service.get_asset(created.id)

    assert result == created


def test_get_asset_raises_when_asset_does_not_exist() -> None:
    service, _repository = make_service()
    unknown_id = uuid4()

    with pytest.raises(
        EntityNotFoundError,
        match=f"Asset not found: {unknown_id}",
    ):
        service.get_asset(unknown_id)


def test_list_assets_returns_all_assets() -> None:
    service, _repository = make_service()
    first = service.create_asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
    )
    second = service.create_asset(
        symbol="BBRI",
        name="Bank Rakyat Indonesia",
        currency="IDR",
    )

    result = service.list_assets()

    assert result == (first, second)


def test_list_assets_returns_empty_tuple() -> None:
    service, _repository = make_service()

    result = service.list_assets()

    assert result == ()


def test_update_asset_replaces_requested_fields() -> None:
    service, repository = make_service()
    existing = service.create_asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
    )
    update_service = AssetService(
        repository=repository,
        clock=lambda: UPDATED_AT,
    )

    result = update_service.update_asset(
        existing.id,
        symbol="bca",
        name="PT Bank Central Asia",
    )

    assert result.id == existing.id
    assert result.symbol == "BCA"
    assert result.name == "PT Bank Central Asia"
    assert result.currency == existing.currency
    assert result.created_at == existing.created_at
    assert result.updated_at == UPDATED_AT
    assert repository.get(existing.id) == result


def test_update_asset_rejects_empty_update() -> None:
    service, _repository = make_service()
    existing = service.create_asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
    )

    with pytest.raises(
        DomainValidationError,
        match="At least one Asset field must be provided",
    ):
        service.update_asset(existing.id)


def test_update_asset_raises_when_asset_does_not_exist() -> None:
    service, _repository = make_service()
    unknown_id = uuid4()

    with pytest.raises(
        EntityNotFoundError,
        match=f"Asset not found: {unknown_id}",
    ):
        service.update_asset(
            unknown_id,
            name="Unknown Asset",
        )


def test_update_asset_rejects_symbol_owned_by_another_asset() -> None:
    service, _repository = make_service()
    first = service.create_asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
    )
    service.create_asset(
        symbol="BBRI",
        name="Bank Rakyat Indonesia",
        currency="IDR",
    )

    with pytest.raises(
        DuplicateEntityError,
        match="Asset symbol already exists: BBRI",
    ):
        service.update_asset(
            first.id,
            symbol="bbri",
        )


def test_delete_asset_removes_existing_asset() -> None:
    service, repository = make_service()
    existing = service.create_asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
    )

    service.delete_asset(existing.id)

    assert repository.get(existing.id) is None


def test_delete_asset_raises_when_asset_does_not_exist() -> None:
    service, _repository = make_service()
    unknown_id = uuid4()

    with pytest.raises(
        EntityNotFoundError,
        match=f"Asset not found: {unknown_id}",
    ):
        service.delete_asset(unknown_id)
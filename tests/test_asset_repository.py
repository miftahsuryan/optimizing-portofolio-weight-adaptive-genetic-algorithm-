from uuid import uuid4

import pytest

from portfolio_optimization.domain import Asset
from portfolio_optimization.exceptions import DuplicateEntityError
from portfolio_optimization.repositories.in_memory import (
    InMemoryAssetRepository,
)


def make_asset(
    *,
    symbol: str = "BBCA",
    name: str = "Bank Central Asia",
) -> Asset:
    return Asset(
        symbol=symbol,
        name=name,
        currency="IDR",
    )


def test_create_stores_and_returns_asset() -> None:
    repository = InMemoryAssetRepository()
    asset = make_asset()

    result = repository.create(asset)

    assert result == asset
    assert repository.get(asset.id) == asset


def test_get_returns_none_for_unknown_id() -> None:
    repository = InMemoryAssetRepository()

    result = repository.get(uuid4())

    assert result is None


def test_get_by_symbol_finds_asset_case_insensitively() -> None:
    repository = InMemoryAssetRepository()
    asset = repository.create(make_asset())

    result = repository.get_by_symbol(" bbca ")

    assert result == asset


def test_get_by_symbol_returns_none_for_unknown_symbol() -> None:
    repository = InMemoryAssetRepository()

    result = repository.get_by_symbol("UNKNOWN")

    assert result is None


def test_list_all_returns_assets_in_creation_order() -> None:
    repository = InMemoryAssetRepository()
    first = repository.create(make_asset())
    second = repository.create(
        make_asset(
            symbol="BBRI",
            name="Bank Rakyat Indonesia",
        )
    )

    result = repository.list_all()

    assert result == (first, second)


def test_create_rejects_duplicate_id() -> None:
    repository = InMemoryAssetRepository()
    asset = repository.create(make_asset())
    duplicate = Asset(
        id=asset.id,
        symbol="BBRI",
        name="Bank Rakyat Indonesia",
        currency="IDR",
    )

    with pytest.raises(
        DuplicateEntityError,
        match=f"Asset ID already exists: {asset.id}",
    ):
        repository.create(duplicate)


def test_create_rejects_duplicate_symbol() -> None:
    repository = InMemoryAssetRepository()
    repository.create(make_asset())

    with pytest.raises(
        DuplicateEntityError,
        match="Asset symbol already exists: BBCA",
    ):
        repository.create(
            make_asset(
                symbol="bbca",
                name="Another Asset",
            )
        )


def test_update_replaces_existing_asset() -> None:
    repository = InMemoryAssetRepository()
    existing = repository.create(make_asset())
    updated = Asset(
        id=existing.id,
        symbol=existing.symbol,
        name="PT Bank Central Asia",
        currency=existing.currency,
        created_at=existing.created_at,
    )

    result = repository.update(updated)

    assert result == updated
    assert repository.get(existing.id) == updated


def test_update_returns_none_for_unknown_asset() -> None:
    repository = InMemoryAssetRepository()
    unknown = make_asset()

    result = repository.update(unknown)

    assert result is None


def test_update_rejects_symbol_owned_by_another_asset() -> None:
    repository = InMemoryAssetRepository()
    first = repository.create(make_asset())
    repository.create(
        make_asset(
            symbol="BBRI",
            name="Bank Rakyat Indonesia",
        )
    )
    conflicting_update = Asset(
        id=first.id,
        symbol="BBRI",
        name=first.name,
        currency=first.currency,
        created_at=first.created_at,
    )

    with pytest.raises(
        DuplicateEntityError,
        match="Asset symbol already exists: BBRI",
    ):
        repository.update(conflicting_update)


def test_delete_removes_existing_asset() -> None:
    repository = InMemoryAssetRepository()
    asset = repository.create(make_asset())

    result = repository.delete(asset.id)

    assert result is True
    assert repository.get(asset.id) is None


def test_delete_returns_false_for_unknown_asset() -> None:
    repository = InMemoryAssetRepository()

    result = repository.delete(uuid4())

    assert result is False


def test_repository_instances_do_not_share_state() -> None:
    first_repository = InMemoryAssetRepository()
    second_repository = InMemoryAssetRepository()
    asset = first_repository.create(make_asset())

    assert first_repository.get(asset.id) == asset
    assert second_repository.get(asset.id) is None
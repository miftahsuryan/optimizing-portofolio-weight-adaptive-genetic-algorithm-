from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from uuid import UUID

from portfolio_optimization.domain import Asset, utc_now
from portfolio_optimization.exceptions import (
    DomainValidationError,
    DuplicateEntityError,
    EntityNotFoundError,
)
from portfolio_optimization.repositories.protocols import AssetRepository


class AssetService:
    """Coordinate Asset business operations."""

    def __init__(
        self,
        repository: AssetRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._clock = clock

    def create_asset(
        self,
        *,
        symbol: str,
        name: str,
        currency: str,
    ) -> Asset:
        now = self._clock()
        asset = Asset(
            symbol=symbol,
            name=name,
            currency=currency,
            created_at=now,
            updated_at=now,
        )

        existing = self._repository.get_by_symbol(asset.symbol)
        if existing is not None:
            raise DuplicateEntityError(
                f"Asset symbol already exists: {asset.symbol}"
            )

        return self._repository.create(asset)

    def get_asset(self, asset_id: UUID) -> Asset:
        asset = self._repository.get(asset_id)

        if asset is None:
            raise EntityNotFoundError(
                f"Asset not found: {asset_id}"
            )

        return asset

    def list_assets(self) -> tuple[Asset, ...]:
        return self._repository.list_all()

    def update_asset(
        self,
        asset_id: UUID,
        *,
        symbol: str | None = None,
        name: str | None = None,
        currency: str | None = None,
    ) -> Asset:
        if symbol is None and name is None and currency is None:
            raise DomainValidationError(
                "At least one Asset field must be provided"
            )

        existing = self.get_asset(asset_id)

        normalized_symbol = (
            symbol.strip().upper()
            if symbol is not None
            else existing.symbol
        )

        symbol_owner = self._repository.get_by_symbol(normalized_symbol)
        if symbol_owner is not None and symbol_owner.id != asset_id:
            raise DuplicateEntityError(
                f"Asset symbol already exists: {normalized_symbol}"
            )

        updated = replace(
            existing,
            symbol=normalized_symbol,
            name=name if name is not None else existing.name,
            currency=(
                currency
                if currency is not None
                else existing.currency
            ),
            updated_at=self._clock(),
        )

        result = self._repository.update(updated)

        if result is None:
            raise EntityNotFoundError(
                f"Asset not found: {asset_id}"
            )

        return result

    def delete_asset(self, asset_id: UUID) -> None:
        deleted = self._repository.delete(asset_id)

        if not deleted:
            raise EntityNotFoundError(
                f"Asset not found: {asset_id}"
            )
from collections.abc import Callable, Iterable
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from portfolio_optimization.domain import (
    PriceReading,
    utc_now,
)
from portfolio_optimization.exceptions import (
    DomainValidationError,
    EntityNotFoundError,
)
from portfolio_optimization.repositories.protocols import (
    AssetRepository,
    PriceReadingRepository,
)


PriceReadingValue = tuple[datetime, Decimal]


class PriceReadingService:
    """Coordinate PriceReading business operations."""

    def __init__(
        self,
        *,
        asset_repository: AssetRepository,
        reading_repository: PriceReadingRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._asset_repository = asset_repository
        self._reading_repository = reading_repository
        self._clock = clock

    def create_reading(
        self,
        *,
        asset_id: UUID,
        observed_at: datetime,
        close: Decimal,
    ) -> PriceReading:
        self._ensure_asset_exists(asset_id)

        reading = PriceReading(
            asset_id=asset_id,
            observed_at=observed_at,
            close=close,
            created_at=self._clock(),
        )
        return self._reading_repository.create(reading)

    def create_readings(
        self,
        *,
        asset_id: UUID,
        values: Iterable[PriceReadingValue],
    ) -> tuple[PriceReading, ...]:
        self._ensure_asset_exists(asset_id)

        batch = tuple(values)
        if not batch:
            raise DomainValidationError(
                "At least one PriceReading must be provided"
            )

        created_at = self._clock()
        readings = tuple(
            PriceReading(
                asset_id=asset_id,
                observed_at=observed_at,
                close=close,
                created_at=created_at,
            )
            for observed_at, close in batch
        )

        return self._reading_repository.create_many(readings)

    def get_reading(self, reading_id: UUID) -> PriceReading:
        reading = self._reading_repository.get(reading_id)

        if reading is None:
            raise EntityNotFoundError(
                f"PriceReading not found: {reading_id}"
            )

        return reading

    def list_readings(
        self,
        asset_id: UUID,
    ) -> tuple[PriceReading, ...]:
        self._ensure_asset_exists(asset_id)
        return self._reading_repository.list_for_asset(asset_id)

    def delete_reading(self, reading_id: UUID) -> None:
        deleted = self._reading_repository.delete(reading_id)

        if not deleted:
            raise EntityNotFoundError(
                f"PriceReading not found: {reading_id}"
            )

    def _ensure_asset_exists(self, asset_id: UUID) -> None:
        if self._asset_repository.get(asset_id) is None:
            raise EntityNotFoundError(
                f"Asset not found: {asset_id}"
            )
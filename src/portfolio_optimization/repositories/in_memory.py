from collections.abc import Iterable
from datetime import datetime
from uuid import UUID

from decimal import Decimal

from portfolio_optimization.domain import (
    Allocation,
    Asset,
    OptimizationRun,
    OptimizationStatus,
    PriceReading,
)
from portfolio_optimization.exceptions import (
    DomainValidationError,
    DuplicateEntityError,
)


class InMemoryAssetRepository:
    """Store Assets in process memory."""

    def __init__(self) -> None:
        self._assets: dict[UUID, Asset] = {}
        self._asset_ids_by_symbol: dict[str, UUID] = {}

    def create(self, asset: Asset) -> Asset:
        if asset.id in self._assets:
            raise DuplicateEntityError(
                f"Asset ID already exists: {asset.id}"
            )

        if asset.symbol in self._asset_ids_by_symbol:
            raise DuplicateEntityError(
                f"Asset symbol already exists: {asset.symbol}"
            )

        self._assets[asset.id] = asset
        self._asset_ids_by_symbol[asset.symbol] = asset.id
        return asset

    def get(self, asset_id: UUID) -> Asset | None:
        return self._assets.get(asset_id)

    def get_by_symbol(self, symbol: str) -> Asset | None:
        normalized_symbol = symbol.strip().upper()
        asset_id = self._asset_ids_by_symbol.get(normalized_symbol)

        if asset_id is None:
            return None

        return self._assets[asset_id]

    def list_all(self) -> tuple[Asset, ...]:
        return tuple(self._assets.values())

    def update(self, asset: Asset) -> Asset | None:
        existing = self._assets.get(asset.id)

        if existing is None:
            return None

        symbol_owner_id = self._asset_ids_by_symbol.get(asset.symbol)
        if symbol_owner_id is not None and symbol_owner_id != asset.id:
            raise DuplicateEntityError(
                f"Asset symbol already exists: {asset.symbol}"
            )

        if existing.symbol != asset.symbol:
            del self._asset_ids_by_symbol[existing.symbol]
            self._asset_ids_by_symbol[asset.symbol] = asset.id

        self._assets[asset.id] = asset
        return asset

    def delete(self, asset_id: UUID) -> bool:
        asset = self._assets.pop(asset_id, None)

        if asset is None:
            return False

        del self._asset_ids_by_symbol[asset.symbol]
        return True


class InMemoryPriceReadingRepository:
    """Store PriceReadings in process memory."""

    def __init__(self) -> None:
        self._readings: dict[UUID, PriceReading] = {}
        self._reading_ids_by_asset_and_time: dict[
            tuple[UUID, datetime],
            UUID,
        ] = {}

    def create(self, reading: PriceReading) -> PriceReading:
        return self.create_many((reading,))[0]

    def create_many(
        self,
        readings: Iterable[PriceReading],
    ) -> tuple[PriceReading, ...]:
        batch = tuple(readings)

        known_ids = set(self._readings)
        known_asset_times = set(
            self._reading_ids_by_asset_and_time
        )

        for reading in batch:
            if reading.id in known_ids:
                raise DuplicateEntityError(
                    f"PriceReading ID already exists: {reading.id}"
                )

            key = (reading.asset_id, reading.observed_at)
            if key in known_asset_times:
                raise DuplicateEntityError(
                    "PriceReading already exists for Asset "
                    f"{reading.asset_id} at "
                    f"{reading.observed_at.isoformat()}"
                )

            known_ids.add(reading.id)
            known_asset_times.add(key)

        for reading in batch:
            key = (reading.asset_id, reading.observed_at)
            self._readings[reading.id] = reading
            self._reading_ids_by_asset_and_time[key] = reading.id

        return batch

    def get(self, reading_id: UUID) -> PriceReading | None:
        return self._readings.get(reading_id)

    def list_for_asset(
        self,
        asset_id: UUID,
    ) -> tuple[PriceReading, ...]:
        readings = (
            reading
            for reading in self._readings.values()
            if reading.asset_id == asset_id
        )
        return tuple(
            sorted(
                readings,
                key=lambda reading: reading.observed_at,
            )
        )

    def delete(self, reading_id: UUID) -> bool:
        reading = self._readings.pop(reading_id, None)

        if reading is None:
            return False

        key = (reading.asset_id, reading.observed_at)
        del self._reading_ids_by_asset_and_time[key]
        return True


class InMemoryOptimizationRepository:
    """Atomically store completed OptimizationRuns and Allocations."""

    def __init__(self) -> None:
        self._runs: dict[UUID, OptimizationRun] = {}
        self._allocations: dict[UUID, Allocation] = {}
        self._allocation_ids_by_run_and_asset: dict[
            tuple[UUID, UUID], UUID
        ] = {}

    def create_completed(
        self,
        run: OptimizationRun,
        allocations: Iterable[Allocation],
    ) -> tuple[OptimizationRun, tuple[Allocation, ...]]:
        batch = tuple(allocations)
        if run.status is not OptimizationStatus.COMPLETED:
            raise DomainValidationError("OptimizationRun must be completed")
        if run.id in self._runs:
            raise DuplicateEntityError(
                f"OptimizationRun ID already exists: {run.id}"
            )
        if not batch:
            raise DomainValidationError(
                "A completed OptimizationRun requires Allocations"
            )

        known_allocation_ids = set(self._allocations)
        known_pairs = set(self._allocation_ids_by_run_and_asset)
        for allocation in batch:
            if allocation.optimization_run_id != run.id:
                raise DomainValidationError(
                    "Allocation must belong to its OptimizationRun"
                )
            if allocation.id in known_allocation_ids:
                raise DuplicateEntityError(
                    f"Allocation ID already exists: {allocation.id}"
                )
            pair = (run.id, allocation.asset_id)
            if pair in known_pairs:
                raise DuplicateEntityError(
                    "Allocation already exists for Asset in OptimizationRun"
                )
            known_allocation_ids.add(allocation.id)
            known_pairs.add(pair)

        total_weight = sum(
            (allocation.weight for allocation in batch),
            start=Decimal("0"),
        )
        if abs(total_weight - Decimal("1")) > Decimal("0.000000001"):
            raise DomainValidationError("Allocation weights must total one")

        self._runs[run.id] = run
        for allocation in batch:
            self._allocations[allocation.id] = allocation
            self._allocation_ids_by_run_and_asset[
                (run.id, allocation.asset_id)
            ] = allocation.id
        return run, batch

    def get(self, run_id: UUID) -> OptimizationRun | None:
        return self._runs.get(run_id)

    def list_all(self) -> tuple[OptimizationRun, ...]:
        return tuple(self._runs.values())

    def list_allocations(
        self,
        run_id: UUID,
    ) -> tuple[Allocation, ...]:
        return tuple(
            allocation
            for allocation in self._allocations.values()
            if allocation.optimization_run_id == run_id
        )

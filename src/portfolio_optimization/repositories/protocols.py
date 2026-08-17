from collections.abc import Iterable
from typing import Protocol
from uuid import UUID

from portfolio_optimization.domain import (
    Allocation,
    Asset,
    OptimizationRun,
    PriceReading,
)


class AssetRepository(Protocol):
    """Storage operations required by the Asset domain service."""

    def create(self, asset: Asset) -> Asset:
        """Store and return a new Asset."""
        ...

    def get(self, asset_id: UUID) -> Asset | None:
        """Return an Asset by ID, or None when it does not exist."""
        ...

    def get_by_symbol(self, symbol: str) -> Asset | None:
        """Return an Asset by symbol, or None when it does not exist."""
        ...

    def list_all(self) -> tuple[Asset, ...]:
        """Return all stored Assets."""
        ...

    def update(self, asset: Asset) -> Asset | None:
        """Replace an existing Asset, or return None when it does not exist."""
        ...

    def delete(self, asset_id: UUID) -> bool:
        """Delete an Asset and report whether it existed."""
        ...


class PriceReadingRepository(Protocol):
    """Storage operations required by the PriceReading service."""

    def create(self, reading: PriceReading) -> PriceReading:
        """Store and return one PriceReading."""
        ...

    def create_many(
        self,
        readings: Iterable[PriceReading],
    ) -> tuple[PriceReading, ...]:
        """Atomically store multiple PriceReadings."""
        ...

    def get(self, reading_id: UUID) -> PriceReading | None:
        """Return a PriceReading by ID."""
        ...

    def list_for_asset(
        self,
        asset_id: UUID,
    ) -> tuple[PriceReading, ...]:
        """Return an Asset's readings in chronological order."""
        ...

    def delete(self, reading_id: UUID) -> bool:
        """Delete a PriceReading and report whether it existed."""
        ...


class OptimizationRepository(Protocol):
    """Atomic storage operations for optimization results."""

    def create_completed(
        self,
        run: OptimizationRun,
        allocations: Iterable[Allocation],
    ) -> tuple[OptimizationRun, tuple[Allocation, ...]]:
        """Atomically store a completed run and its allocations."""
        ...

    def get(self, run_id: UUID) -> OptimizationRun | None:
        """Return an OptimizationRun by ID."""
        ...

    def list_all(self) -> tuple[OptimizationRun, ...]:
        """Return all OptimizationRuns."""
        ...

    def list_allocations(
        self,
        run_id: UUID,
    ) -> tuple[Allocation, ...]:
        """Return all Allocations for an OptimizationRun."""
        ...

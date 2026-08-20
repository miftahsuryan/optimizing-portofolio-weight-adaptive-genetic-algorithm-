"""PostgreSQL adapters for the domain repository protocols."""

from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from portfolio_optimization.domain import (
    Allocation,
    Asset,
    OptimizationRun,
    OptimizationStatus,
    PriceReading,
)
from portfolio_optimization.exceptions import DomainValidationError
from portfolio_optimization.repositories.models import (
    AllocationRow,
    AssetRow,
    OptimizationRunRow,
    PriceReadingRow,
)


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def _asset(row: AssetRow) -> Asset:
    return Asset(
        id=row.id, symbol=row.symbol, name=row.name, currency=row.currency,
        created_at=_aware(row.created_at), updated_at=_aware(row.updated_at),
    )


def _reading(row: PriceReadingRow) -> PriceReading:
    return PriceReading(
        id=row.id, asset_id=row.asset_id, observed_at=_aware(row.observed_at),
        close=row.close, created_at=_aware(row.created_at),
    )


def _run(row: OptimizationRunRow) -> OptimizationRun:
    return OptimizationRun(
        id=row.id, method=row.method, status=OptimizationStatus(row.status),
        start_date=row.start_date, end_date=row.end_date,
        expected_return=row.expected_return, volatility=row.volatility,
        sharpe_ratio=row.sharpe_ratio, best_fitness=row.best_fitness,
        population_size=row.population_size, generations=row.generations,
        max_weight=row.max_weight,
        diversification_penalty=row.diversification_penalty,
        crossover_rate=row.crossover_rate, mutation_rate=row.mutation_rate,
        seed=row.seed, convergence_generation=row.convergence_generation,
        runtime_seconds=row.runtime_seconds, created_at=_aware(row.created_at),
        completed_at=_aware(row.completed_at),
    )


def _allocation(row: AllocationRow) -> Allocation:
    return Allocation(
        id=row.id, optimization_run_id=row.optimization_run_id,
        asset_id=row.asset_id, weight=row.weight,
        created_at=_aware(row.created_at),
    )


class PostgresAssetRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, asset: Asset) -> Asset:
        self._session.add(AssetRow(**{
            "id": asset.id, "symbol": asset.symbol, "name": asset.name,
            "currency": asset.currency, "created_at": asset.created_at,
            "updated_at": asset.updated_at,
        }))
        self._session.flush()
        return asset

    def get(self, asset_id: UUID) -> Asset | None:
        row = self._session.get(AssetRow, asset_id)
        return _asset(row) if row is not None else None

    def get_by_symbol(self, symbol: str) -> Asset | None:
        row = self._session.scalar(
            select(AssetRow).where(AssetRow.symbol == symbol.strip().upper())
        )
        return _asset(row) if row is not None else None

    def list_all(self) -> tuple[Asset, ...]:
        rows = self._session.scalars(
            select(AssetRow).order_by(AssetRow.created_at, AssetRow.id)
        )
        return tuple(_asset(row) for row in rows)

    def update(self, asset: Asset) -> Asset | None:
        result = self._session.execute(
            update(AssetRow).where(AssetRow.id == asset.id).values(
                symbol=asset.symbol, name=asset.name, currency=asset.currency,
                updated_at=asset.updated_at,
            )
        )
        self._session.flush()
        return asset if result.rowcount else None

    def delete(self, asset_id: UUID) -> bool:
        result = self._session.execute(
            delete(AssetRow).where(AssetRow.id == asset_id)
        )
        self._session.flush()
        return bool(result.rowcount)


class PostgresPriceReadingRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, reading: PriceReading) -> PriceReading:
        return self.create_many((reading,))[0]

    def create_many(self, readings: Iterable[PriceReading]) -> tuple[PriceReading, ...]:
        batch = tuple(readings)
        self._session.add_all([
            PriceReadingRow(
                id=item.id, asset_id=item.asset_id,
                observed_at=item.observed_at, close=item.close,
                created_at=item.created_at,
            ) for item in batch
        ])
        self._session.flush()
        return batch

    def get(self, reading_id: UUID) -> PriceReading | None:
        row = self._session.get(PriceReadingRow, reading_id)
        return _reading(row) if row is not None else None

    def list_for_asset(self, asset_id: UUID) -> tuple[PriceReading, ...]:
        rows = self._session.scalars(
            select(PriceReadingRow).where(
                PriceReadingRow.asset_id == asset_id
            ).order_by(PriceReadingRow.observed_at, PriceReadingRow.id)
        )
        return tuple(_reading(row) for row in rows)

    def delete(self, reading_id: UUID) -> bool:
        result = self._session.execute(
            delete(PriceReadingRow).where(PriceReadingRow.id == reading_id)
        )
        self._session.flush()
        return bool(result.rowcount)


class PostgresOptimizationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_completed(
        self, run: OptimizationRun, allocations: Iterable[Allocation]
    ) -> tuple[OptimizationRun, tuple[Allocation, ...]]:
        batch = tuple(allocations)
        if run.status is not OptimizationStatus.COMPLETED:
            raise DomainValidationError("OptimizationRun must be completed")
        if not batch:
            raise DomainValidationError(
                "A completed OptimizationRun requires Allocations"
            )
        if any(item.optimization_run_id != run.id for item in batch):
            raise DomainValidationError(
                "Allocation must belong to its OptimizationRun"
            )
        total = sum((item.weight for item in batch), Decimal("0"))
        if abs(total - Decimal("1")) > Decimal("0.000000001"):
            raise DomainValidationError("Allocation weights must total one")
        self._session.add(OptimizationRunRow(**{
            field: getattr(run, field) for field in (
                "id", "method", "status", "start_date", "end_date",
                "expected_return", "volatility", "sharpe_ratio",
                "best_fitness", "population_size", "generations",
                "max_weight", "diversification_penalty", "crossover_rate",
                "mutation_rate", "seed", "convergence_generation",
                "runtime_seconds", "created_at", "completed_at",
            )
        }))
        self._session.add_all([
            AllocationRow(
                id=item.id, optimization_run_id=item.optimization_run_id,
                asset_id=item.asset_id, weight=item.weight,
                created_at=item.created_at,
            ) for item in batch
        ])
        self._session.flush()
        return run, batch

    def get(self, run_id: UUID) -> OptimizationRun | None:
        row = self._session.get(OptimizationRunRow, run_id)
        return _run(row) if row is not None else None

    def list_all(self) -> tuple[OptimizationRun, ...]:
        rows = self._session.scalars(
            select(OptimizationRunRow).order_by(
                OptimizationRunRow.created_at, OptimizationRunRow.id
            )
        )
        return tuple(_run(row) for row in rows)

    def list_allocations(self, run_id: UUID) -> tuple[Allocation, ...]:
        rows = self._session.scalars(
            select(AllocationRow).where(
                AllocationRow.optimization_run_id == run_id
            ).order_by(AllocationRow.created_at, AllocationRow.id)
        )
        return tuple(_allocation(row) for row in rows)

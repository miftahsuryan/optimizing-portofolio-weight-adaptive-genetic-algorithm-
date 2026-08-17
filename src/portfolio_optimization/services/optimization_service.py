from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from time import perf_counter
from uuid import UUID

import numpy as np
import pandas as pd

from portfolio_optimization.domain import (
    Allocation,
    OptimizationRun,
    utc_now,
)
from portfolio_optimization.exceptions import (
    DomainValidationError,
    EntityNotFoundError,
)
from portfolio_optimization.optimization.sga import SGAConfig, run_sga
from portfolio_optimization.repositories.protocols import (
    AssetRepository,
    OptimizationRepository,
    PriceReadingRepository,
)


@dataclass(frozen=True, slots=True)
class CompletedOptimization:
    run: OptimizationRun
    allocations: tuple[Allocation, ...]


class OptimizationService:
    """Prepare price data, execute SGA, and persist its result."""

    def __init__(
        self,
        *,
        asset_repository: AssetRepository,
        reading_repository: PriceReadingRepository,
        optimization_repository: OptimizationRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._asset_repository = asset_repository
        self._reading_repository = reading_repository
        self._optimization_repository = optimization_repository
        self._clock = clock

    def optimize_sga(
        self,
        *,
        asset_ids: Iterable[UUID],
        start_date: date,
        end_date: date,
        config: SGAConfig,
    ) -> CompletedOptimization:
        selected_ids = tuple(asset_ids)
        if len(selected_ids) != len(set(selected_ids)):
            raise DomainValidationError("asset_ids must be unique")
        if start_date > end_date:
            raise DomainValidationError(
                "start_date must not be later than end_date"
            )

        assets = []
        rows: list[dict[str, object]] = []
        for asset_id in selected_ids:
            asset = self._asset_repository.get(asset_id)
            if asset is None:
                raise EntityNotFoundError(f"Asset not found: {asset_id}")
            assets.append(asset)
            readings = (
                reading
                for reading in self._reading_repository.list_for_asset(asset_id)
                if start_date <= reading.observed_at.date() <= end_date
            )
            rows.extend(
                {
                    "Date": reading.observed_at,
                    "ticker": asset.symbol,
                    "Close": float(reading.close),
                }
                for reading in readings
            )

        if len(assets) < 2:
            raise DomainValidationError("At least two Assets are required")
        prices = pd.DataFrame(rows)
        if prices.empty:
            raise DomainValidationError(
                "No PriceReadings are available in the requested period"
            )
        matrix = prices.pivot(index="Date", columns="ticker", values="Close")
        expected_symbols = [asset.symbol for asset in assets]
        missing = set(expected_symbols) - set(matrix.columns)
        if missing:
            raise DomainValidationError(
                f"Assets without PriceReadings: {sorted(missing)}"
            )
        returns = matrix[expected_symbols].sort_index().pct_change().dropna()
        if len(returns) < 2:
            raise DomainValidationError(
                "At least three aligned price observations are required"
            )
        mean_returns = returns.mean().to_numpy(dtype=float)
        covariance = returns.cov().to_numpy(dtype=float)

        started = perf_counter()
        result = run_sga(mean_returns, covariance, config)
        runtime = perf_counter() - started
        now = self._clock()
        run = OptimizationRun(
            start_date=start_date,
            end_date=end_date,
            expected_return=self._decimal(result.expected_return),
            volatility=self._decimal(result.volatility),
            sharpe_ratio=self._decimal(result.sharpe_ratio),
            best_fitness=self._decimal(result.best_fitness),
            population_size=config.population_size,
            generations=config.generations,
            max_weight=self._decimal(config.max_weight),
            diversification_penalty=self._decimal(
                config.diversification_penalty
            ),
            crossover_rate=self._decimal(config.crossover_rate),
            mutation_rate=self._decimal(config.mutation_rate),
            seed=config.seed,
            convergence_generation=result.convergence_generation,
            runtime_seconds=self._decimal(runtime),
            created_at=now,
            completed_at=now,
        )
        decimal_weights = [
            self._decimal(weight) for weight in result.weights[:-1]
        ]
        decimal_weights.append(Decimal("1") - sum(decimal_weights, Decimal("0")))
        allocations = tuple(
            Allocation(
                optimization_run_id=run.id,
                asset_id=asset.id,
                weight=weight,
                created_at=now,
            )
            for asset, weight in zip(assets, decimal_weights, strict=True)
        )
        stored_run, stored_allocations = (
            self._optimization_repository.create_completed(run, allocations)
        )
        return CompletedOptimization(stored_run, stored_allocations)

    def get_optimization(self, run_id: UUID) -> CompletedOptimization:
        run = self._optimization_repository.get(run_id)
        if run is None:
            raise EntityNotFoundError(
                f"OptimizationRun not found: {run_id}"
            )
        return CompletedOptimization(
            run,
            self._optimization_repository.list_allocations(run_id),
        )

    def list_optimizations(self) -> tuple[CompletedOptimization, ...]:
        return tuple(
            CompletedOptimization(
                run,
                self._optimization_repository.list_allocations(run.id),
            )
            for run in self._optimization_repository.list_all()
        )

    @staticmethod
    def _decimal(value: float) -> Decimal:
        if not np.isfinite(value):
            raise DomainValidationError("Optimization result must be finite")
        return Decimal(str(float(value)))

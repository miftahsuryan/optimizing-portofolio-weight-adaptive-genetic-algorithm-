from datetime import UTC, date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from portfolio_optimization.domain import Allocation, OptimizationRun
from portfolio_optimization.exceptions import DomainValidationError
from portfolio_optimization.repositories.in_memory import (
    InMemoryOptimizationRepository,
)


NOW = datetime(2026, 8, 17, 10, 0, tzinfo=UTC)


def make_run() -> OptimizationRun:
    return OptimizationRun(
        start_date=date(2026, 8, 1),
        end_date=date(2026, 8, 17),
        expected_return=Decimal("0.01"),
        volatility=Decimal("0.02"),
        sharpe_ratio=Decimal("0.5"),
        best_fitness=Decimal("-0.49"),
        population_size=20,
        generations=10,
        max_weight=Decimal("0.6"),
        diversification_penalty=Decimal("0.1"),
        crossover_rate=Decimal("0.9"),
        mutation_rate=Decimal("0.1"),
        seed=29,
        convergence_generation=4,
        runtime_seconds=Decimal("0.01"),
        created_at=NOW,
        completed_at=NOW,
    )


def allocation(
    run_id: UUID,
    asset_id: UUID,
    weight: str,
) -> Allocation:
    return Allocation(
        optimization_run_id=run_id,
        asset_id=asset_id,
        weight=Decimal(weight),
        created_at=NOW,
    )


def test_store_completed_run_and_allocations_atomically() -> None:
    repository = InMemoryOptimizationRepository()
    run = make_run()
    allocations = (
        allocation(run.id, uuid4(), "0.6"),
        allocation(run.id, uuid4(), "0.4"),
    )

    result = repository.create_completed(run, allocations)

    assert result == (run, allocations)
    assert repository.get(run.id) == run
    assert repository.list_allocations(run.id) == allocations


def test_invalid_total_is_not_partially_persisted() -> None:
    repository = InMemoryOptimizationRepository()
    run = make_run()
    allocations = (
        allocation(run.id, uuid4(), "0.6"),
        allocation(run.id, uuid4(), "0.3"),
    )

    with pytest.raises(
        DomainValidationError,
        match="Allocation weights must total one",
    ):
        repository.create_completed(run, allocations)

    assert repository.get(run.id) is None
    assert repository.list_allocations(run.id) == ()


def test_allocation_for_another_run_is_not_persisted() -> None:
    repository = InMemoryOptimizationRepository()
    run = make_run()

    with pytest.raises(
        DomainValidationError,
        match="Allocation must belong",
    ):
        repository.create_completed(
            run,
            (allocation(uuid4(), uuid4(), "1"),),
        )

    assert repository.get(run.id) is None

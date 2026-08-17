from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from portfolio_optimization.domain.common import utc_now
from portfolio_optimization.exceptions import DomainValidationError


class OptimizationStatus(StrEnum):
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class OptimizationRun:
    """A completed execution of a portfolio optimization algorithm."""

    start_date: date
    end_date: date
    expected_return: Decimal
    volatility: Decimal
    sharpe_ratio: Decimal
    best_fitness: Decimal
    population_size: int
    generations: int
    max_weight: Decimal
    diversification_penalty: Decimal
    crossover_rate: Decimal
    mutation_rate: Decimal
    seed: int
    convergence_generation: int
    runtime_seconds: Decimal
    id: UUID = field(default_factory=uuid4)
    method: str = "SGA"
    status: OptimizationStatus = OptimizationStatus.COMPLETED
    created_at: datetime = field(default_factory=utc_now)
    completed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.start_date > self.end_date:
            raise DomainValidationError(
                "start_date must not be later than end_date"
            )
        if self.method != "SGA":
            raise DomainValidationError("method must be SGA")
        if self.status is not OptimizationStatus.COMPLETED:
            raise DomainValidationError("status must be completed")
        if self.population_size < 3:
            raise DomainValidationError("population_size must be at least 3")
        if self.generations < 1:
            raise DomainValidationError("generations must be positive")
        if self.convergence_generation < 0:
            raise DomainValidationError(
                "convergence_generation must not be negative"
            )
        for name in ("max_weight", "crossover_rate", "mutation_rate"):
            value = getattr(self, name)
            if not value.is_finite() or not Decimal("0") < value <= Decimal("1"):
                raise DomainValidationError(
                    f"{name} must be between zero and one"
                )
        completed_at = self.completed_at or self.created_at
        if completed_at.tzinfo is None or completed_at.utcoffset() is None:
            raise DomainValidationError("completed_at must be timezone-aware")
        object.__setattr__(self, "completed_at", completed_at)


@dataclass(frozen=True, slots=True)
class Allocation:
    """The weight assigned to one Asset by an OptimizationRun."""

    optimization_run_id: UUID
    asset_id: UUID
    weight: Decimal
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if (
            not self.weight.is_finite()
            or not Decimal("0") <= self.weight <= Decimal("1")
        ):
            raise DomainValidationError("weight must be between zero and one")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise DomainValidationError("created_at must be timezone-aware")

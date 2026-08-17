from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SGAOptimizationRequest(BaseModel):
    asset_ids: list[UUID] = Field(min_length=2)
    start_date: date
    end_date: date
    population_size: int = Field(default=100, ge=3, le=10_000)
    generations: int = Field(default=100, ge=1, le=10_000)
    max_weight: float = Field(default=0.3, gt=0, le=1)
    diversification_penalty: float = Field(default=0.1, ge=0)
    crossover_rate: float = Field(default=0.9, ge=0, le=1)
    mutation_rate: float = Field(default=0.1, ge=0, le=1)
    mutation_scale: float = Field(default=0.05, gt=0)
    tournament_size: int = Field(default=3, ge=2)
    seed: int = 29


class AllocationResponse(BaseModel):
    id: UUID
    asset_id: UUID
    weight: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OptimizationRunResponse(BaseModel):
    id: UUID
    method: str
    status: str
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
    created_at: datetime
    completed_at: datetime
    allocations: list[AllocationResponse]

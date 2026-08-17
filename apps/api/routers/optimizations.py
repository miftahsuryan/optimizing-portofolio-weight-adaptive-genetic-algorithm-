from uuid import UUID

from fastapi import APIRouter, status

from apps.api.dependencies import OptimizationServiceDependency
from apps.api.schemas import (
    AllocationResponse,
    ErrorResponse,
    OptimizationRunResponse,
    SGAOptimizationRequest,
)
from portfolio_optimization.optimization.sga import SGAConfig
from portfolio_optimization.services.optimization_service import (
    CompletedOptimization,
)


router = APIRouter(prefix="/optimizations", tags=["optimizations"])


def to_response(result: CompletedOptimization) -> OptimizationRunResponse:
    run = result.run
    return OptimizationRunResponse(
        id=run.id,
        method=run.method,
        status=run.status,
        start_date=run.start_date,
        end_date=run.end_date,
        expected_return=run.expected_return,
        volatility=run.volatility,
        sharpe_ratio=run.sharpe_ratio,
        best_fitness=run.best_fitness,
        population_size=run.population_size,
        generations=run.generations,
        max_weight=run.max_weight,
        diversification_penalty=run.diversification_penalty,
        crossover_rate=run.crossover_rate,
        mutation_rate=run.mutation_rate,
        seed=run.seed,
        convergence_generation=run.convergence_generation,
        runtime_seconds=run.runtime_seconds,
        created_at=run.created_at,
        completed_at=run.completed_at,
        allocations=[
            AllocationResponse.model_validate(allocation)
            for allocation in result.allocations
        ],
    )


@router.post(
    "/sga",
    response_model=OptimizationRunResponse,
    status_code=status.HTTP_201_CREATED,
    responses={404: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
)
def optimize_sga(
    request: SGAOptimizationRequest,
    service: OptimizationServiceDependency,
) -> OptimizationRunResponse:
    config = SGAConfig(
        population_size=request.population_size,
        generations=request.generations,
        max_weight=request.max_weight,
        diversification_penalty=request.diversification_penalty,
        crossover_rate=request.crossover_rate,
        mutation_rate=request.mutation_rate,
        mutation_scale=request.mutation_scale,
        tournament_size=request.tournament_size,
        seed=request.seed,
    )
    return to_response(
        service.optimize_sga(
            asset_ids=request.asset_ids,
            start_date=request.start_date,
            end_date=request.end_date,
            config=config,
        )
    )


@router.get("", response_model=list[OptimizationRunResponse])
def list_optimizations(
    service: OptimizationServiceDependency,
) -> list[OptimizationRunResponse]:
    return [to_response(result) for result in service.list_optimizations()]


@router.get(
    "/{run_id}",
    response_model=OptimizationRunResponse,
    responses={404: {"model": ErrorResponse}},
)
def get_optimization(
    run_id: UUID,
    service: OptimizationServiceDependency,
) -> OptimizationRunResponse:
    return to_response(service.get_optimization(run_id))

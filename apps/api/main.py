from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routers.briefs import router as briefs_router
from apps.api.routers.assets import router as assets_router
from apps.api.routers.price_readings import (
    router as price_readings_router,
)
from apps.api.routers.optimizations import router as optimizations_router
from apps.api.schemas import (
    ErrorDetail,
    ErrorResponse,
    PortfolioAnalysisResponse,
)
from portfolio_optimization.config import load_config
from portfolio_optimization.database import ping_database
from portfolio_optimization.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    PortfolioOptimizationError,
)
from portfolio_optimization.services.analysis_service import (
    analyze_portfolio,
)


app = FastAPI(title="Portfolio Optimization API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
app.include_router(briefs_router)
app.include_router(assets_router)
app.include_router(price_readings_router)
app.include_router(optimizations_router)


def error_response(
    error: PortfolioOptimizationError,
    *,
    status_code: int,
) -> JSONResponse:
    response = ErrorResponse(
        error=ErrorDetail(
            code=error.code,
            message=str(error),
        ),
    )
    return JSONResponse(
        status_code=status_code,
        content=response.model_dump(),
    )


@app.exception_handler(EntityNotFoundError)
async def entity_not_found_error_handler(
    _request: Request,
    error: EntityNotFoundError,
) -> JSONResponse:
    return error_response(error, status_code=404)


@app.exception_handler(DuplicateEntityError)
async def duplicate_entity_error_handler(
    _request: Request,
    error: DuplicateEntityError,
) -> JSONResponse:
    return error_response(error, status_code=409)


@app.exception_handler(PortfolioOptimizationError)
async def portfolio_error_handler(
    _request: Request,
    error: PortfolioOptimizationError,
) -> JSONResponse:
    return error_response(error, status_code=422)


@app.exception_handler(FileNotFoundError)
async def file_not_found_error_handler(
    _request: Request,
    error: FileNotFoundError,
) -> JSONResponse:
    response = ErrorResponse(
        error=ErrorDetail(code="data_file_not_found", message=str(error)),
    )
    return JSONResponse(status_code=422, content=response.model_dump())


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def database_health_check() -> dict[str, str]:
    """Verify that the configured database accepts a real query."""
    ping_database()
    return {"status": "ok", "database": "reachable"}


@app.get(
    "/portfolio/analysis",
    response_model=PortfolioAnalysisResponse,
    responses={422: {"model": ErrorResponse}},
)
def portfolio_analysis() -> PortfolioAnalysisResponse:
    config = load_config()
    result = analyze_portfolio(config.price_data_path)

    return PortfolioAnalysisResponse(
        summary={
            "rows": result.summary.row_count,
            "tickers": result.summary.ticker_count,
            "start_date": result.summary.start_date.date(),
            "end_date": result.summary.end_date.date(),
            "missing_close": int(result.summary.missing_close_count),
        },
        statistics={
            "mean_returns": result.statistics.mean_returns.to_dict(),
            "covariance_matrix": result.statistics.covariance_matrix.to_dict(),
        },
    )

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from apps.api.schemas import ErrorDetail, ErrorResponse, PortfolioAnalysisResponse
from portfolio_optimization.config import load_config
from portfolio_optimization.exceptions import PortfolioOptimizationError
from portfolio_optimization.services.analysis_service import (
    analyze_portfolio,
)


app = FastAPI(title="Portfolio Optimization API")


@app.exception_handler(PortfolioOptimizationError)
async def portfolio_error_handler(
    _request: Request,
    error: PortfolioOptimizationError,
) -> JSONResponse:
    response = ErrorResponse(
        error=ErrorDetail(code=error.code, message=str(error)),
    )
    return JSONResponse(status_code=422, content=response.model_dump())


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

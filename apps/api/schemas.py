from datetime import date

from pydantic import BaseModel


class DatasetSummaryResponse(BaseModel):
    rows: int
    tickers: int
    start_date: date
    end_date: date
    missing_close: int


class PortfolioStatisticsResponse(BaseModel):
    mean_returns: dict[str, float]
    covariance_matrix: dict[str, dict[str, float]]


class PortfolioAnalysisResponse(BaseModel):
    summary: DatasetSummaryResponse
    statistics: PortfolioStatisticsResponse


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail

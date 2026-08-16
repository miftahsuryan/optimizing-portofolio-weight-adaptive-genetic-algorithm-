from dataclasses import dataclass
from pathlib import Path

from portfolio_optimization.compute_statistic.portfolio_statistics import (
    PortfolioStatistics,
    compute_portfolio_statistics,
)
from portfolio_optimization.ingestion.load_prices import load_price_data
from portfolio_optimization.services.summary_service import (
    DatasetSummary,
    summarize_price_data,
)


@dataclass(frozen=True)
class PortfolioAnalysis:
    summary: DatasetSummary
    statistics: PortfolioStatistics


def analyze_portfolio(csv_path: Path) -> PortfolioAnalysis:
    price_data = load_price_data(csv_path)

    return PortfolioAnalysis(
        summary=summarize_price_data(price_data),
        statistics=compute_portfolio_statistics(price_data),
    )
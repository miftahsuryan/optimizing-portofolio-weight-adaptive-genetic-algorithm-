import sys

from portfolio_optimization.compute_statistic.portfolio_statistics import (
    compute_portfolio_statistics,
)
from portfolio_optimization.config import load_config
from portfolio_optimization.exceptions import PortfolioOptimizationError
from portfolio_optimization.ingestion.load_constituents import (
    load_constituent_matrix,
)
from portfolio_optimization.ingestion.load_prices import load_price_data
from portfolio_optimization.preprocessing.idx30_intersection import (
    filter_prices_by_tickers,
    find_consistent_tickers,
)
from portfolio_optimization.services.summary_service import (
    summarize_price_data,
)


def main() -> int:
    """Run the local portfolio-data summary workflow."""
    try:
        config = load_config()
        price_data = load_price_data(config.price_data_path)
        constituent_data = load_constituent_matrix(
            config.idx30_constituents_path
        )
        consistent_tickers = find_consistent_tickers(constituent_data)
        price_data = filter_prices_by_tickers(
            price_data,
            consistent_tickers,
        )
        summary = summarize_price_data(price_data)
        statistics = compute_portfolio_statistics(price_data)
    except (FileNotFoundError, PortfolioOptimizationError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("Consistent IDX30 Dataset Summary")
    print(f"Periods     : {len(constituent_data.columns) - 1}")
    print(f"Rows        : {summary.row_count}")
    print(f"Tickers     : {summary.ticker_count}")
    print(f"Start date  : {summary.start_date.date()}")
    print(f"End date    : {summary.end_date.date()}")
    print(f"Missing     : {summary.missing_close_count}")
    print("Portfolio Statistics")
    print(f"Return rows : {len(statistics.daily_returns)}")
    print(f"Assets      : {len(statistics.mean_returns)}")
    print(
        "Covariance  : "
        f"{statistics.covariance_matrix.shape[0]} x "
        f"{statistics.covariance_matrix.shape[1]}"
    )

    return 0

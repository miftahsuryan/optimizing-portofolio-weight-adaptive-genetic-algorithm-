import sys

from portfolio_optimization.config import load_config
from portfolio_optimization.exceptions import PortfolioOptimizationError
from portfolio_optimization.ingestion.load_csv import load_price_data
from portfolio_optimization.services.summary_service import (
    summarize_price_data,
)


def main() -> int:
    """Run the local portfolio-data summary workflow."""
    try:
        config = load_config()
        price_data = load_price_data(config.price_data_path)
        summary = summarize_price_data(price_data)
    except (FileNotFoundError, PortfolioOptimizationError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("Dataset Summary")
    print(f"Rows        : {summary.row_count}")
    print(f"Tickers     : {summary.ticker_count}")
    print(f"Start date  : {summary.start_date.date()}")
    print(f"End date    : {summary.end_date.date()}")
    print(f"Missing     : {summary.missing_close_count}")

    return 0

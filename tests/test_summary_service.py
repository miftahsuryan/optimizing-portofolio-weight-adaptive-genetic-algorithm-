from pathlib import Path

import pandas as pd

from portfolio_optimization.ingestion.load_prices import load_price_data
from portfolio_optimization.services.summary_service import (
    DatasetSummary,
    summarize_price_data,
)


def test_summarize_price_data_returns_correct_summary() -> None:
    price_data = load_price_data(
        Path("tests/fixtures/prices_valid.csv")
    )

    summary = summarize_price_data(price_data)

    assert isinstance(summary, DatasetSummary)
    assert summary.row_count == 6
    assert summary.ticker_count == 2
    assert summary.start_date == pd.Timestamp("2025-01-02")
    assert summary.end_date == pd.Timestamp("2025-01-06")
    assert summary.missing_close_count == 0
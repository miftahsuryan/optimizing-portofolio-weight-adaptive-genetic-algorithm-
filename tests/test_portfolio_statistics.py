from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimization.analytics.portfolio_statistics import (
    PortfolioStatistics,
    compute_portfolio_statistics,
)
from portfolio_optimization.ingestion.load_prices import load_price_data


def test_compute_portfolio_statistics() -> None:
    """Validated prices should produce optimization-ready statistics."""
    price_data = load_price_data(Path("tests/fixtures/prices_valid.csv"))

    result = compute_portfolio_statistics(price_data)

    assert isinstance(result, PortfolioStatistics)
    assert result.daily_returns.shape == (2, 2)
    assert result.daily_returns.columns.tolist() == ["AAA", "BBB"]
    assert result.mean_returns.index.tolist() == ["AAA", "BBB"]
    assert result.covariance_matrix.shape == (2, 2)


def test_daily_returns_are_calculated_per_ticker() -> None:
    """A ticker's return must use its own preceding closing price."""
    price_data = load_price_data(Path("tests/fixtures/prices_valid.csv"))

    result = compute_portfolio_statistics(price_data)

    expected_aaa = (105.0 - 100.0) / 100.0
    expected_bbb = (190.0 - 200.0) / 200.0
    first_return_date = pd.Timestamp("2025-01-03")
    assert result.daily_returns.loc[
        first_return_date,
        "AAA",
    ] == pytest.approx(expected_aaa)
    assert result.daily_returns.loc[
        first_return_date,
        "BBB",
    ] == pytest.approx(expected_bbb)

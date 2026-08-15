from pathlib import Path

import pandas as pd

from portfolio_optimization.ingestion.load_constituents import (
    load_constituent_matrix,
)
from portfolio_optimization.ingestion.load_prices import load_price_data
from portfolio_optimization.preprocessing.idx30_intersection import (
    filter_prices_by_tickers,
    find_consistent_tickers,
)


def test_find_consistent_tickers_uses_all_periods() -> None:
    constituent_data = load_constituent_matrix(
        Path("tests/fixtures/idx30_constituents_valid.csv")
    )

    result = find_consistent_tickers(constituent_data)

    assert result == ("BBCA", "BBRI")


def test_filter_prices_keeps_only_consistent_tickers() -> None:
    price_data = load_price_data(Path("tests/fixtures/prices_valid.csv"))

    result = filter_prices_by_tickers(price_data, ("BBCA",))

    assert isinstance(result, pd.DataFrame)
    assert result["ticker"].unique().tolist() == ["BBCA"]
    assert len(result) == 3

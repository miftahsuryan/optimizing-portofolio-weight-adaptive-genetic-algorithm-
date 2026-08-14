from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class DatasetSummary:
    row_count: int
    ticker_count: int
    start_date: pd.Timestamp
    end_date: pd.Timestamp
    missing_close_count: int


def summarize_price_data(
    price_data: pd.DataFrame,
) -> DatasetSummary:
    """Calculate a concise summary of validated price data."""
    return DatasetSummary(
        row_count=len(price_data),
        ticker_count=price_data["ticker"].nunique(),
        start_date=price_data["Date"].min(),
        end_date=price_data["Date"].max(),
        missing_close_count=price_data["Close"].isna().sum(),
    )
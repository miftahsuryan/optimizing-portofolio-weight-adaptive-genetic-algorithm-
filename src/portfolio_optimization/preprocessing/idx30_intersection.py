from collections.abc import Iterable

import pandas as pd

from portfolio_optimization.exceptions import DataValidationError


def find_consistent_tickers(
    constituent_data: pd.DataFrame,
) -> tuple[str, ...]:
    """Find tickers present in every constituent period column."""
    period_columns = [
        column for column in constituent_data.columns if column != "No"
    ]
    if not period_columns:
        raise DataValidationError(
            "IDX30 constituent data must contain period columns."
        )

    ticker_sets = []
    for column in period_columns:
        tickers = {
            str(ticker).strip().upper()
            for ticker in constituent_data[column].dropna()
            if str(ticker).strip()
        }
        if not tickers:
            raise DataValidationError(
                f"IDX30 constituent period must not be empty: {column}"
            )
        ticker_sets.append(tickers)

    consistent_tickers = sorted(set.intersection(*ticker_sets))
    if not consistent_tickers:
        raise DataValidationError(
            "No ticker is present in every IDX30 constituent period."
        )

    return tuple(consistent_tickers)


def filter_prices_by_tickers(
    price_data: pd.DataFrame,
    tickers: Iterable[str],
) -> pd.DataFrame:
    """Keep price observations belonging to the selected tickers."""
    selected_tickers = {ticker.strip().upper() for ticker in tickers}
    available_tickers = set(price_data["ticker"].dropna().astype(str))
    missing_tickers = selected_tickers - available_tickers
    if missing_tickers:
        raise DataValidationError(
            "Consistent IDX30 tickers missing from price data: "
            f"{sorted(missing_tickers)}"
        )

    return (
        price_data[price_data["ticker"].isin(selected_tickers)]
        .copy()
        .reset_index(drop=True)
    )

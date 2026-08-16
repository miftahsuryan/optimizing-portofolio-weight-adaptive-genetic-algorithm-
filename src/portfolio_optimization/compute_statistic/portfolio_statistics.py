from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class PortfolioStatistics:
    """Statistical inputs required by portfolio optimization."""
    daily_returns: pd.DataFrame
    mean_returns: pd.Series
    covariance_matrix: pd.DataFrame


def calculate_daily_return(
    current_price: float,
    previous_price: float,
) -> float:
    """Calculate one simple return from two closing prices."""
    if not isinstance(current_price, (int, float)) or not isinstance(
        previous_price,
        (int, float),
    ):
        raise TypeError("Prices must be numeric values.")

    if current_price <= 0.0:
        raise ValueError("Current price must be greater than zero.")

    if previous_price <= 0.0:
        raise ValueError("Previous price must be greater than zero.")

    return (current_price - previous_price) / previous_price


def compute_portfolio_statistics(
    price_data: pd.DataFrame,
) -> PortfolioStatistics:
    """Calculate daily returns, mean returns, and return covariance.

    Returns are calculated independently for each ticker. Missing observations
    are retained so assets with different listing periods can still contribute
    all of their available history to the mean and covariance calculations.
    """
    returns_data = price_data[["Date", "ticker", "Close"]].copy()
    returns_data["daily_return"] = returns_data.groupby(
        "ticker",
        sort=False,
    )["Close"].pct_change(fill_method=None)

    daily_returns = (
        returns_data.pivot(
            index="Date",
            columns="ticker",
            values="daily_return",
        )
        .sort_index()
        .dropna(how="all")
    )
    daily_returns.columns.name = None

    return PortfolioStatistics(
        daily_returns=daily_returns,
        mean_returns=daily_returns.mean(),
        covariance_matrix=daily_returns.cov(),
    )

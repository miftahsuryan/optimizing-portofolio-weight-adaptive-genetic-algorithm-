from pathlib import Path

import pandas as pd

from portfolio_optimization.exceptions import DataValidationError


REQUIRED_COLUMNS = {"Date", "ticker", "Close"}


def load_price_data(csv_path: Path) -> pd.DataFrame:
    """Load and validate price data from a CSV file.

    Args:
        csv_path: Path to the CSV file.

    Returns:
        The validated price data.

    Raises:
        FileNotFoundError: If the CSV file does not exist.
        DataValidationError: If the CSV data is empty or invalid.
    """
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Price data file not found: {csv_path}"
        )

    try:
        price_data = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError as error:
        raise DataValidationError("Price data must not be empty.") from error

    if price_data.empty:
        raise DataValidationError("Price data must not be empty.")

    missing_columns = REQUIRED_COLUMNS - set(price_data.columns)

    if missing_columns:
        raise DataValidationError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    try:
        price_data["Date"] = pd.to_datetime(
            price_data["Date"],
            errors="raise",
        )
    except (TypeError, ValueError) as error:
        raise DataValidationError("Invalid Date values.") from error

    if price_data["Date"].isna().any():
        raise DataValidationError("Invalid Date values.")

    try:
        price_data["Close"] = pd.to_numeric(
            price_data["Close"],
            errors="raise",
        )
    except (TypeError, ValueError) as error:
        raise DataValidationError("Invalid Close values.") from error

    non_missing_close = price_data["Close"].dropna()
    if (non_missing_close <= 0).any():
        raise DataValidationError("Close values must be positive.")

    return price_data.sort_values(
        ["Date", "ticker"],
    ).reset_index(drop=True)

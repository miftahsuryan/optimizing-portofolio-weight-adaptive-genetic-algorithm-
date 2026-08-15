from pathlib import Path

import pandas as pd

from portfolio_optimization.exceptions import DataValidationError


def load_constituent_matrix(csv_path: Path) -> pd.DataFrame:
    """Load an IDX30 constituent matrix whose columns represent periods."""
    if not csv_path.exists():
        raise FileNotFoundError(
            f"IDX30 constituent file not found: {csv_path}"
        )

    try:
        constituent_data = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError as error:
        raise DataValidationError(
            "IDX30 constituent data must not be empty."
        ) from error

    if constituent_data.empty:
        raise DataValidationError(
            "IDX30 constituent data must not be empty."
        )

    period_columns = [
        column for column in constituent_data.columns if column != "No"
    ]
    if not period_columns:
        raise DataValidationError(
            "IDX30 constituent data must contain period columns."
        )

    return constituent_data

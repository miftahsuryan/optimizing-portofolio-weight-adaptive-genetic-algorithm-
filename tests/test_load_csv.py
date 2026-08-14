from pathlib import Path

import pandas as pd
import pytest

from portfolio_optimization.exceptions import DataValidationError
from portfolio_optimization.ingestion.load_csv import load_price_data


def test_load_price_data_returns_valid_dataframe() -> None:
    """Valid CSV should produce a DataFrame."""
    result = load_price_data(
        Path("tests/fixtures/prices_valid.csv")
    )

    assert isinstance(result, pd.DataFrame)
    assert len(result) == 6
    assert pd.api.types.is_datetime64_any_dtype(result["Date"])
    assert pd.api.types.is_numeric_dtype(result["Close"])
    assert result.equals(
        result.sort_values(["Date", "ticker"]).reset_index(drop=True)
    )


def test_load_price_data_rejects_missing_file(tmp_path: Path) -> None:
    """A missing CSV file should produce a clear file error."""
    missing_file = tmp_path / "not_found.csv"

    with pytest.raises(
        FileNotFoundError,
        match="Price data file not found",
    ):
        load_price_data(missing_file)


def test_load_price_data_rejects_missing_columns() -> None:
    """CSV without required columns should be rejected."""
    with pytest.raises(
        DataValidationError,
        match="Missing required columns",
    ):
        load_price_data(
            Path("tests/fixtures/prices_missing_column.csv")
        )


def test_load_price_data_rejects_empty_csv(tmp_path: Path) -> None:
    """A CSV containing only headers should be rejected."""
    empty_csv = tmp_path / "prices_empty.csv"
    empty_csv.write_text("Date,ticker,Close\n", encoding="utf-8")

    with pytest.raises(
        DataValidationError,
        match="Price data must not be empty",
    ):
        load_price_data(empty_csv)


def test_load_price_data_rejects_invalid_date(tmp_path: Path) -> None:
    """An invalid date value should be rejected."""
    invalid_date_csv = tmp_path / "prices_invalid_date.csv"
    invalid_date_csv.write_text(
        "Date,ticker,Close\nnot-a-date,BBCA,9675\n",
        encoding="utf-8",
    )

    with pytest.raises(
        DataValidationError,
        match="Invalid Date values",
    ):
        load_price_data(invalid_date_csv)


def test_load_price_data_rejects_invalid_close(tmp_path: Path) -> None:
    """A non-numeric closing price should be rejected."""
    invalid_close_csv = tmp_path / "prices_invalid_close.csv"
    invalid_close_csv.write_text(
        "Date,ticker,Close\n2025-01-02,BBCA,invalid\n",
        encoding="utf-8",
    )

    with pytest.raises(
        DataValidationError,
        match="Invalid Close values",
    ):
        load_price_data(invalid_close_csv)


@pytest.mark.parametrize("close", [0, -100])
def test_load_price_data_rejects_non_positive_close(
    tmp_path: Path,
    close: int,
) -> None:
    """Zero and negative closing prices should be rejected."""
    invalid_close_csv = tmp_path / "prices_non_positive_close.csv"
    invalid_close_csv.write_text(
        f"Date,ticker,Close\n2025-01-02,BBCA,{close}\n",
        encoding="utf-8",
    )

    with pytest.raises(
        DataValidationError,
        match="Close values must be positive",
    ):
        load_price_data(invalid_close_csv)
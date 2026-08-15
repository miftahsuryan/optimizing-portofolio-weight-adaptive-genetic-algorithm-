from pathlib import Path

import pytest

from portfolio_optimization.cli import main


def test_cli_success(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """CLI should summarize valid price data and return exit code 0."""
    monkeypatch.setenv(
        "PRICE_DATA_PATH",
        "tests/fixtures/prices_valid.csv",
    )
    monkeypatch.setenv(
        "IDX30_CONSTITUENTS_PATH",
        "tests/fixtures/idx30_constituents_valid.csv",
    )

    result = main()

    assert result == 0

    output = capsys.readouterr()
    assert output.err == ""
    assert output.out.splitlines() == [
        "Consistent IDX30 Dataset Summary",
        "Periods     : 3",
        "Rows        : 6",
        "Tickers     : 2",
        "Start date  : 2025-01-02",
        "End date    : 2025-01-06",
        "Missing     : 0",
        "Portfolio Statistics",
        "Return rows : 2",
        "Assets      : 2",
        "Covariance  : 2 x 2",
    ]


def test_cli_returns_error_when_price_file_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """CLI should report a missing input file and return exit code 1."""
    missing_file = tmp_path / "prices_not_found.csv"
    monkeypatch.setenv("PRICE_DATA_PATH", str(missing_file))

    result = main()

    output = capsys.readouterr()
    assert result == 1
    assert output.out == ""
    assert output.err == f"Error: Price data file not found: {missing_file}\n"


def test_cli_returns_error_when_price_data_is_invalid(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """CLI should report invalid CSV data and return exit code 1."""
    monkeypatch.setenv(
        "PRICE_DATA_PATH",
        "tests/fixtures/prices_missing_column.csv",
    )

    result = main()

    output = capsys.readouterr()
    assert result == 1
    assert output.out == ""
    assert "Error: Missing required columns:" in output.err

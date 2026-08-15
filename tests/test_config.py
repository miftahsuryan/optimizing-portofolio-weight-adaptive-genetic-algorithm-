from pathlib import Path

import pytest

from portfolio_optimization.config import load_config


def test_load_config_uses_environment_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.setenv(
        "PRICE_DATA_PATH",
        "tests/fixtures/prices_valid.csv",
    )
    monkeypatch.setenv(
        "IDX30_CONSTITUENTS_PATH",
        "tests/fixtures/idx30_constituents_valid.csv",
    )

    # Act
    config = load_config()

    # Assert
    assert config.price_data_path == Path(
        "tests/fixtures/prices_valid.csv"
    )
    assert config.idx30_constituents_path == Path(
        "tests/fixtures/idx30_constituents_valid.csv"
    )


def test_load_config_uses_default_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.delenv(
        "PRICE_DATA_PATH",
        raising=False,
    )
    monkeypatch.delenv(
        "IDX30_CONSTITUENTS_PATH",
        raising=False,
    )

    # Act
    config = load_config()

    # Assert
    assert config.price_data_path == Path(
        "data/idx30_close_prices_daily_2023-2026_raw.csv"
    )
    assert config.idx30_constituents_path == Path(
        "data/List_IDX30_Lengkap_2022_2026.xlsx - Matriks 2022-2026.csv"
    )

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

    # Act
    config = load_config()

    # Assert
    assert config.price_data_path == Path(
        "tests/fixtures/prices_valid.csv"
    )


def test_load_config_uses_default_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.delenv(
        "PRICE_DATA_PATH",
        raising=False,
    )

    # Act
    config = load_config()

    # Assert
    assert config.price_data_path == Path("data/prices.csv")
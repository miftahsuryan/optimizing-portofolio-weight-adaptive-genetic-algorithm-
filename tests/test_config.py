from pathlib import Path

import pytest

from portfolio_optimization.config import load_config
from portfolio_optimization.exceptions import ConfigurationError


def test_load_config_uses_environment_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Arrange
    monkeypatch.setenv(
        "PRICE_DATA_PATH",
        "tests/fixtures/prices_valid.csv",
    )
    # Act
    config = load_config(env_file=None)

    # Assert
    assert config.price_data_path == Path(
        "tests/fixtures/prices_valid.csv"
    )


def test_load_config_raises_domain_error_when_path_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PRICE_DATA_PATH", raising=False)

    with pytest.raises(
        ConfigurationError,
        match="Invalid application configuration",
    ):
        load_config(env_file=None)

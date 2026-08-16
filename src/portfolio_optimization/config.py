from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from portfolio_optimization.exceptions import ConfigurationError


class AppConfig(BaseSettings):
    price_data_path: Path

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
    )


def load_config(
    *,
    env_file: str | Path | None = ".env",
) -> AppConfig:
    """Load validated settings from environment variables and an env file."""
    try:
        return AppConfig(_env_file=env_file)
    except ValidationError as error:
        raise ConfigurationError("Invalid application configuration.") from error

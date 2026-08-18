from pathlib import Path

from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

from portfolio_optimization.exceptions import ConfigurationError


class DatabaseConfig(BaseSettings):
    database_url: str = (
        "postgresql+psycopg://portfolio:portfolio@localhost:5432/portfolio"
    )
    database_echo: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
    )


class AppConfig(DatabaseConfig):
    price_data_path: Path


def load_config(
    *,
    env_file: str | Path | None = ".env",
) -> AppConfig:
    """Load validated settings from environment variables and an env file."""
    try:
        return AppConfig(_env_file=env_file)
    except ValidationError as error:
        raise ConfigurationError("Invalid application configuration.") from error


def load_database_config(
    *,
    env_file: str | Path | None = ".env",
) -> DatabaseConfig:
    """Load database settings independently from data-analysis settings."""
    try:
        return DatabaseConfig(_env_file=env_file)
    except ValidationError as error:
        raise ConfigurationError("Invalid database configuration.") from error

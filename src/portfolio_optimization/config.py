import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class AppConfig:
    """Application Configuration"""
    price_data_path: Path

def load_config() -> AppConfig:
    """Load application configuration from environment variables"""
    price_data_path = os.getenv(
        "PRICE_DATA_PATH",
        "data/prices.csv"
    )

    return AppConfig(
        price_data_path=Path(price_data_path)
    )
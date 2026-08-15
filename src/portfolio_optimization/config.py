import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class AppConfig:
    """Application Configuration"""
    price_data_path: Path
    idx30_constituents_path: Path

def load_config() -> AppConfig:
    """Load application configuration from environment variables"""
    price_data_path = os.getenv(
        "PRICE_DATA_PATH",
        "data/idx30_close_prices_daily_2023-2026_raw.csv",
    )
    idx30_constituents_path = os.getenv(
        "IDX30_CONSTITUENTS_PATH",
        "data/List_IDX30_Lengkap_2022_2026.xlsx - Matriks 2022-2026.csv",
    )

    return AppConfig(
        price_data_path=Path(price_data_path),
        idx30_constituents_path=Path(idx30_constituents_path),
    )

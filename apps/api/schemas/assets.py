from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AssetCreateRequest(BaseModel):
    symbol: str = Field(min_length=1)
    name: str = Field(min_length=1)
    currency: str = Field(
        min_length=3,
        max_length=3,
        pattern=r"^[A-Za-z]{3}$",
    )
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str) -> str:
        return value.upper()

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class AssetUpdateRequest(BaseModel):
    symbol: str | None = Field(default=None, min_length=1)
    name: str | None = Field(default=None, min_length=1)
    currency: str | None = Field(
        default=None,
        min_length=3,
        max_length=3,
        pattern=r"^[A-Za-z]{3}$",
    )
    model_config = ConfigDict(str_strip_whitespace=True)

    @field_validator("symbol")
    @classmethod
    def normalize_symbol(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str | None) -> str | None:
        return value.upper() if value is not None else None


class AssetResponse(BaseModel):
    id: UUID
    symbol: str
    name: str
    currency: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

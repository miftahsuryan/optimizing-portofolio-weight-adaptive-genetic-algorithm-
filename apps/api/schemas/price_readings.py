from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PriceReadingCreateRequest(BaseModel):
    observed_at: datetime
    close: Decimal = Field(gt=0)


class PriceReadingBatchCreateRequest(BaseModel):
    readings: list[PriceReadingCreateRequest] = Field(min_length=1)


class PriceReadingResponse(BaseModel):
    id: UUID
    asset_id: UUID
    observed_at: datetime
    close: Decimal
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

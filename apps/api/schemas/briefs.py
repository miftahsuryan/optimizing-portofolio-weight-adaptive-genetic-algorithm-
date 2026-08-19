from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from portfolio_optimization.domain import RiskProfile


class PortfolioBriefCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    risk_profile: RiskProfile


class PortfolioBriefResponse(BaseModel):
    id: UUID
    name: str
    risk_profile: RiskProfile
    ai_summary: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


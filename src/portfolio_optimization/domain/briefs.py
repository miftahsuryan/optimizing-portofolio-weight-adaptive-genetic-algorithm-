from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from portfolio_optimization.domain.common import utc_now
from portfolio_optimization.exceptions import DomainValidationError


class RiskProfile(StrEnum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    GROWTH = "growth"


@dataclass(frozen=True, slots=True)
class PortfolioBrief:
    """One persisted request and its deterministic AI-stub response."""

    name: str
    risk_profile: RiskProfile
    ai_summary: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        normalized_name = self.name.strip()
        if not normalized_name:
            raise DomainValidationError("name must not be empty")
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise DomainValidationError("created_at must be timezone-aware")
        object.__setattr__(self, "name", normalized_name)


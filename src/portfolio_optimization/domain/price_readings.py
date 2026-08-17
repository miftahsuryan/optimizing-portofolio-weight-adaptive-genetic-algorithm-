from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from portfolio_optimization.domain.common import utc_now
from portfolio_optimization.exceptions import DomainValidationError


@dataclass(frozen=True, slots=True)
class PriceReading:
    """A historical price observation for an Asset."""

    asset_id: UUID
    observed_at: datetime
    close: Decimal
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not isinstance(self.asset_id, UUID):
            raise DomainValidationError("asset_id must be a UUID")
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise DomainValidationError("observed_at must be timezone-aware")
        if not isinstance(self.close, Decimal):
            raise DomainValidationError("close must be a Decimal")
        if not self.close.is_finite() or self.close <= Decimal("0"):
            raise DomainValidationError(
                "close must be a finite positive number"
            )
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise DomainValidationError("created_at must be timezone-aware")

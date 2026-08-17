from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from portfolio_optimization.domain.common import utc_now
from portfolio_optimization.exceptions import DomainValidationError


@dataclass(frozen=True, slots=True)
class Asset:
    """An investable instrument in the portfolio domain."""

    symbol: str
    name: str
    currency: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        normalized_symbol = self.symbol.strip().upper()
        normalized_currency = self.currency.strip().upper()
        normalized_name = self.name.strip()
        if not normalized_symbol:
            raise DomainValidationError("symbol must not be empty")
        if not normalized_name:
            raise DomainValidationError("name must not be empty")
        if not normalized_currency:
            raise DomainValidationError("currency must not be empty")
        if len(normalized_currency) != 3 or not normalized_currency.isalpha():
            raise DomainValidationError(
                "currency must be a three-letter alphabetic code"
            )
        if self.created_at.tzinfo is None or self.created_at.utcoffset() is None:
            raise DomainValidationError("created_at must be timezone-aware")
        updated_at = self.updated_at or self.created_at
        if updated_at.tzinfo is None or updated_at.utcoffset() is None:
            raise DomainValidationError("updated_at must be timezone-aware")
        object.__setattr__(self, "symbol", normalized_symbol)
        object.__setattr__(self, "name", normalized_name)
        object.__setattr__(self, "currency", normalized_currency)
        object.__setattr__(self, "updated_at", updated_at)

from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from portfolio_optimization.domain import PriceReading
from portfolio_optimization.exceptions import DomainValidationError


OBSERVED_AT = datetime(2026, 8, 17, 9, 0, tzinfo=UTC)
CREATED_AT = datetime(2026, 8, 17, 10, 0, tzinfo=UTC)


def test_price_reading_accepts_valid_data() -> None:
    asset_id = uuid4()

    reading = PriceReading(
        asset_id=asset_id,
        observed_at=OBSERVED_AT,
        close=Decimal("8500.50"),
        created_at=CREATED_AT,
    )

    assert reading.asset_id == asset_id
    assert reading.observed_at == OBSERVED_AT
    assert reading.close == Decimal("8500.50")
    assert reading.created_at == CREATED_AT


@pytest.mark.parametrize(
    "close",
    [
        Decimal("0"),
        Decimal("-1"),
        Decimal("NaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
    ],
)
def test_price_reading_rejects_non_positive_or_non_finite_close(
    close: Decimal,
) -> None:
    with pytest.raises(
        DomainValidationError,
        match="close must be a finite positive number",
    ):
        PriceReading(
            asset_id=uuid4(),
            observed_at=OBSERVED_AT,
            close=close,
        )


def test_price_reading_requires_decimal_close() -> None:
    with pytest.raises(
        DomainValidationError,
        match="close must be a Decimal",
    ):
        PriceReading(
            asset_id=uuid4(),
            observed_at=OBSERVED_AT,
            close=8500.50,  # type: ignore[arg-type]
        )


def test_price_reading_rejects_naive_observed_at() -> None:
    naive_datetime = datetime(2026, 8, 17, 9, 0)

    with pytest.raises(
        DomainValidationError,
        match="observed_at must be timezone-aware",
    ):
        PriceReading(
            asset_id=uuid4(),
            observed_at=naive_datetime,
            close=Decimal("8500.50"),
        )


def test_price_reading_rejects_naive_created_at() -> None:
    naive_datetime = datetime(2026, 8, 17, 10, 0)

    with pytest.raises(
        DomainValidationError,
        match="created_at must be timezone-aware",
    ):
        PriceReading(
            asset_id=uuid4(),
            observed_at=OBSERVED_AT,
            close=Decimal("8500.50"),
            created_at=naive_datetime,
        )


def test_price_reading_rejects_invalid_asset_id() -> None:
    with pytest.raises(
        DomainValidationError,
        match="asset_id must be a UUID",
    ):
        PriceReading(
            asset_id="not-a-uuid",  # type: ignore[arg-type]
            observed_at=OBSERVED_AT,
            close=Decimal("8500.50"),
        )
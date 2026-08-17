from datetime import UTC, datetime
from uuid import UUID

import pytest

from portfolio_optimization.exceptions import DomainValidationError
from portfolio_optimization.domain import Asset


def test_asset_normalizes_its_text_fields() -> None:
    """Asset should normalize its text fields."""
    asset = Asset(
        symbol=" bbca ",
        name=" Bank Central Asia ",
        currency="idr ",
    )

    assert isinstance(asset.id, UUID)
    assert asset.symbol == "BBCA"
    assert asset.name == "Bank Central Asia"
    assert asset.currency == "IDR"
    assert asset.created_at.tzinfo is not None
    assert asset.updated_at == asset.created_at


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("symbol", ""),
        ("symbol", "  "),
        ("name", ""),
        ("name", "   "),
        ("currency", ""),
        ("currency", "   "),
    ],
)
def test_asset_rejects_empty_required_fields(
    field_name: str,
    field_value: str,
) -> None:
    values = {
        "symbol": "BBCA",
        "name": "Bank Central Asia",
        "currency": "IDR",
    }
    values[field_name] = field_value

    with pytest.raises(DomainValidationError,
                       match=f"{field_name} must not be empty",
    ):
        Asset(**values)


@pytest.mark.parametrize("currency", ["I", "ID", "IDRR", "123"])
def test_asset_rejects_invalid_currency(currency: str) -> None:
    with pytest.raises(
        DomainValidationError,
        match="currency must be a three-letter alphabetic code",
    ):
        Asset(
            symbol="BBCA",
            name="Bank Central Asia",
            currency=currency,
        )
def test_asset_rejects_naive_created_at() -> None:
    naive_datetime = datetime(2026, 8, 17, 8, 0)

    with pytest.raises(
        DomainValidationError,
        match="created_at must be timezone-aware",
    ):
        Asset(
            symbol="BBCA",
            name="Bank Central Asia",
            currency="IDR",
            created_at=naive_datetime,
        )


def test_asset_accepts_explicit_timezone_aware_created_at() -> None:
    created_at = datetime(2026, 8, 17, 8, 0, tzinfo=UTC)

    asset = Asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
        created_at=created_at,
    )

    assert asset.created_at == created_at
    assert asset.updated_at == created_at

    
def test_asset_rejects_naive_updated_at() -> None:
    naive_datetime = datetime(2026, 8, 17, 8, 0)

    with pytest.raises(
        DomainValidationError,
        match="updated_at must be timezone-aware",
    ):
        Asset(
            symbol="BBCA",
            name="Bank Central Asia",
            currency="IDR",
            updated_at=naive_datetime,
        )
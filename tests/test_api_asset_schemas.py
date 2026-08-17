from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from apps.api.schemas import (
    AssetCreateRequest,
    AssetResponse,
    AssetUpdateRequest,
)
from portfolio_optimization.domain import Asset


def test_asset_create_request_normalizes_input() -> None:
    request = AssetCreateRequest(
        symbol=" bbca ",
        name=" Bank Central Asia ",
        currency=" idr ",
    )

    assert request.symbol == "BBCA"
    assert request.name == "Bank Central Asia"
    assert request.currency == "IDR"


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("symbol", ""),
        ("symbol", "   "),
        ("name", ""),
        ("name", "   "),
        ("currency", ""),
        ("currency", "   "),
    ],
)
def test_asset_create_request_rejects_empty_fields(
    field_name: str,
    field_value: str,
) -> None:
    values = {
        "symbol": "BBCA",
        "name": "Bank Central Asia",
        "currency": "IDR",
    }
    values[field_name] = field_value

    with pytest.raises(ValidationError):
        AssetCreateRequest(**values)


@pytest.mark.parametrize("currency", ["I", "ID", "IDRR", "123"])
def test_asset_create_request_rejects_invalid_currency(
    currency: str,
) -> None:
    with pytest.raises(ValidationError):
        AssetCreateRequest(
            symbol="BBCA",
            name="Bank Central Asia",
            currency=currency,
        )


def test_asset_update_request_allows_partial_update() -> None:
    request = AssetUpdateRequest(name=" Updated Name ")

    assert request.symbol is None
    assert request.name == "Updated Name"
    assert request.currency is None


def test_asset_response_can_be_created_from_domain_entity() -> None:
    timestamp = datetime(2026, 8, 17, 8, 0, tzinfo=UTC)
    asset = Asset(
        symbol="BBCA",
        name="Bank Central Asia",
        currency="IDR",
        created_at=timestamp,
        updated_at=timestamp,
    )

    response = AssetResponse.model_validate(asset)

    assert response.id == asset.id
    assert response.symbol == "BBCA"
    assert response.name == "Bank Central Asia"
    assert response.currency == "IDR"
    assert response.created_at == timestamp
    assert response.updated_at == timestamp
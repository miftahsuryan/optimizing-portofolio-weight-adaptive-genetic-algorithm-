from uuid import UUID

from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from apps.api.dependencies import AssetServiceDependency
from apps.api.schemas import (
    AssetCreateRequest,
    AssetResponse,
    AssetUpdateRequest,
    ErrorResponse,
)


router = APIRouter(
    prefix="/assets",
    tags=["assets"],
)


@router.post(
    "",
    response_model=AssetResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_asset(
    request: AssetCreateRequest,
    service: AssetServiceDependency,
):
    return service.create_asset(
        symbol=request.symbol,
        name=request.name,
        currency=request.currency,
    )


@router.get(
    "",
    response_model=list[AssetResponse],
)
def list_assets(
    service: AssetServiceDependency,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    symbol: Annotated[str | None, Query(min_length=1)] = None,
    currency: Annotated[
        str | None,
        Query(min_length=3, max_length=3, pattern=r"^[A-Za-z]{3}$"),
    ] = None,
):
    assets = service.list_assets()
    if symbol is not None:
        normalized_symbol = symbol.strip().upper()
        assets = tuple(
            asset for asset in assets if asset.symbol == normalized_symbol
        )
    if currency is not None:
        normalized_currency = currency.upper()
        assets = tuple(
            asset for asset in assets if asset.currency == normalized_currency
        )
    return assets[offset : offset + limit]


@router.get(
    "/{asset_id}",
    response_model=AssetResponse,
    responses={
        404: {"model": ErrorResponse},
    },
)
def get_asset(
    asset_id: UUID,
    service: AssetServiceDependency,
):
    return service.get_asset(asset_id)


@router.patch(
    "/{asset_id}",
    response_model=AssetResponse,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def update_asset(
    asset_id: UUID,
    request: AssetUpdateRequest,
    service: AssetServiceDependency,
):
    return service.update_asset(
        asset_id,
        symbol=request.symbol,
        name=request.name,
        currency=request.currency,
    )


@router.delete(
    "/{asset_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse},
    },
)
def delete_asset(
    asset_id: UUID,
    service: AssetServiceDependency,
) -> Response:
    service.delete_asset(asset_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

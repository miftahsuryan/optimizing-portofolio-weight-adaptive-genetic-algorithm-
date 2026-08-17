from uuid import UUID

from fastapi import APIRouter, Response, status

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
):
    return service.list_assets()


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
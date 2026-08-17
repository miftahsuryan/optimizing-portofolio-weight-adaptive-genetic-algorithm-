from uuid import UUID

from fastapi import APIRouter, Response, status

from apps.api.dependencies import PriceReadingServiceDependency
from apps.api.schemas import (
    ErrorResponse,
    PriceReadingBatchCreateRequest,
    PriceReadingCreateRequest,
    PriceReadingResponse,
)


router = APIRouter(tags=["price-readings"])


@router.post(
    "/assets/{asset_id}/readings",
    response_model=PriceReadingResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_reading(
    asset_id: UUID,
    request: PriceReadingCreateRequest,
    service: PriceReadingServiceDependency,
):
    return service.create_reading(
        asset_id=asset_id,
        observed_at=request.observed_at,
        close=request.close,
    )


@router.post(
    "/assets/{asset_id}/readings/batch",
    response_model=list[PriceReadingResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
)
def create_reading_batch(
    asset_id: UUID,
    request: PriceReadingBatchCreateRequest,
    service: PriceReadingServiceDependency,
):
    values = tuple(
        (reading.observed_at, reading.close)
        for reading in request.readings
    )
    return service.create_readings(
        asset_id=asset_id,
        values=values,
    )


@router.get(
    "/assets/{asset_id}/readings",
    response_model=list[PriceReadingResponse],
    responses={
        404: {"model": ErrorResponse},
    },
)
def list_readings(
    asset_id: UUID,
    service: PriceReadingServiceDependency,
):
    return service.list_readings(asset_id)


@router.get(
    "/readings/{reading_id}",
    response_model=PriceReadingResponse,
    responses={
        404: {"model": ErrorResponse},
    },
)
def get_reading(
    reading_id: UUID,
    service: PriceReadingServiceDependency,
):
    return service.get_reading(reading_id)


@router.delete(
    "/readings/{reading_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        404: {"model": ErrorResponse},
    },
)
def delete_reading(
    reading_id: UUID,
    service: PriceReadingServiceDependency,
) -> Response:
    service.delete_reading(reading_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
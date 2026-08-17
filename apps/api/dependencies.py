from typing import Annotated

from fastapi import Depends

from portfolio_optimization.repositories.in_memory import (
    InMemoryAssetRepository,
    InMemoryOptimizationRepository,
    InMemoryPriceReadingRepository,
)
from portfolio_optimization.repositories.protocols import (
    AssetRepository,
    OptimizationRepository,
    PriceReadingRepository,
)
from portfolio_optimization.services.asset_service import AssetService
from portfolio_optimization.services.price_reading_service import (
    PriceReadingService,
)
from portfolio_optimization.services.optimization_service import (
    OptimizationService,
)

_asset_repository = InMemoryAssetRepository()
_price_reading_repository = InMemoryPriceReadingRepository()
_optimization_repository = InMemoryOptimizationRepository()


def get_asset_repository() -> AssetRepository:
    """Return the application Asset repository."""
    return _asset_repository


def get_asset_service(
    repository: Annotated[
        AssetRepository,
        Depends(get_asset_repository),
    ],
) -> AssetService:
    """Build an Asset service from its repository dependency."""
    return AssetService(repository=repository)


AssetServiceDependency = Annotated[
    AssetService,
    Depends(get_asset_service),
]


def get_price_reading_repository() -> PriceReadingRepository:
    """Return the application PriceReading repository."""
    return _price_reading_repository


def get_price_reading_service(
    asset_repository: Annotated[
        AssetRepository,
        Depends(get_asset_repository),
    ],
    reading_repository: Annotated[
        PriceReadingRepository,
        Depends(get_price_reading_repository),
    ],
) -> PriceReadingService:
    """Build a PriceReading service from its dependencies."""
    return PriceReadingService(
        asset_repository=asset_repository,
        reading_repository=reading_repository,
    )


PriceReadingServiceDependency = Annotated[
    PriceReadingService,
    Depends(get_price_reading_service),
]


def get_optimization_repository() -> OptimizationRepository:
    """Return the application Optimization repository."""
    return _optimization_repository


def get_optimization_service(
    asset_repository: Annotated[
        AssetRepository,
        Depends(get_asset_repository),
    ],
    reading_repository: Annotated[
        PriceReadingRepository,
        Depends(get_price_reading_repository),
    ],
    optimization_repository: Annotated[
        OptimizationRepository,
        Depends(get_optimization_repository),
    ],
) -> OptimizationService:
    return OptimizationService(
        asset_repository=asset_repository,
        reading_repository=reading_repository,
        optimization_repository=optimization_repository,
    )


OptimizationServiceDependency = Annotated[
    OptimizationService,
    Depends(get_optimization_service),
]

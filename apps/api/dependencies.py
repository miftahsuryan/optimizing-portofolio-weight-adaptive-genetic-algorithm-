from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from portfolio_optimization.database import get_session

from portfolio_optimization.repositories.postgres import (
    PostgresAssetRepository,
    PostgresOptimizationRepository,
    PostgresPriceReadingRepository,
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

def get_database_session() -> Iterator[Session]:
    """Expose the transaction-scoped database session to API routes."""
    yield from get_session()


def get_asset_repository(
    session: Annotated[Session, Depends(get_database_session)],
) -> AssetRepository:
    """Return the application Asset repository."""
    return PostgresAssetRepository(session)


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


def get_price_reading_repository(
    session: Annotated[Session, Depends(get_database_session)],
) -> PriceReadingRepository:
    """Return the application PriceReading repository."""
    return PostgresPriceReadingRepository(session)


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


def get_optimization_repository(
    session: Annotated[Session, Depends(get_database_session)],
) -> OptimizationRepository:
    """Return the application Optimization repository."""
    return PostgresOptimizationRepository(session)


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

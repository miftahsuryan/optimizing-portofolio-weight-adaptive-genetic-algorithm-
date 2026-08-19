from typing import Annotated

from fastapi import APIRouter, Depends, status

from apps.api.dependencies import get_database_session
from apps.api.schemas.briefs import (
    PortfolioBriefCreateRequest,
    PortfolioBriefResponse,
)
from portfolio_optimization.repositories.postgres_briefs import (
    PostgresPortfolioBriefRepository,
)
from portfolio_optimization.services.brief_service import PortfolioBriefService
from sqlalchemy.orm import Session


router = APIRouter(prefix="/briefs", tags=["briefs"])
DatabaseSession = Annotated[Session, Depends(get_database_session)]


def build_service(session: Session) -> PortfolioBriefService:
    return PortfolioBriefService(PostgresPortfolioBriefRepository(session))


@router.post(
    "",
    response_model=PortfolioBriefResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_brief(
    request: PortfolioBriefCreateRequest,
    session: DatabaseSession,
) -> PortfolioBriefResponse:
    return PortfolioBriefResponse.model_validate(
        build_service(session).create(
            name=request.name,
            risk_profile=request.risk_profile,
        )
    )


@router.get("", response_model=list[PortfolioBriefResponse])
def list_briefs(session: DatabaseSession) -> list[PortfolioBriefResponse]:
    return [
        PortfolioBriefResponse.model_validate(brief)
        for brief in build_service(session).list_all()
    ]


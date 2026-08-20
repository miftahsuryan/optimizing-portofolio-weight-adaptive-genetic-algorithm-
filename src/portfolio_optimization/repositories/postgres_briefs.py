from datetime import UTC

from sqlalchemy import select
from sqlalchemy.orm import Session

from portfolio_optimization.domain import PortfolioBrief, RiskProfile


from portfolio_optimization.repositories.models import Base, PortfolioBriefRow

metadata = Base.metadata


class PostgresPortfolioBriefRepository:
    """Persist portfolio briefs using the request-scoped SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, brief: PortfolioBrief) -> PortfolioBrief:
        self._session.add(
            PortfolioBriefRow(
                id=brief.id,
                name=brief.name,
                risk_profile=brief.risk_profile.value,
                ai_summary=brief.ai_summary,
                created_at=brief.created_at,
            )
        )
        self._session.flush()
        return brief

    def list_all(self) -> tuple[PortfolioBrief, ...]:
        rows = self._session.scalars(
            select(PortfolioBriefRow).order_by(
                PortfolioBriefRow.created_at.desc(),
                PortfolioBriefRow.id.desc(),
            )
        )
        return tuple(
            PortfolioBrief(
                id=row.id,
                name=row.name,
                risk_profile=RiskProfile(row.risk_profile),
                ai_summary=row.ai_summary,
                created_at=(
                    row.created_at.replace(tzinfo=UTC)
                    if row.created_at.tzinfo is None
                    else row.created_at
                ),
            )
            for row in rows
        )

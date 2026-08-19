from datetime import UTC

from sqlalchemy import (
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    Uuid,
    insert,
    select,
)
from sqlalchemy.orm import Session

from portfolio_optimization.domain import PortfolioBrief, RiskProfile


metadata = MetaData()
portfolio_briefs = Table(
    "portfolio_briefs",
    metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("name", String(120), nullable=False),
    Column("risk_profile", String(16), nullable=False),
    Column("ai_summary", String(500), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


class PostgresPortfolioBriefRepository:
    """Persist portfolio briefs using the request-scoped SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, brief: PortfolioBrief) -> PortfolioBrief:
        self._session.execute(
            insert(portfolio_briefs).values(
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
        rows = self._session.execute(
            select(portfolio_briefs).order_by(
                portfolio_briefs.c.created_at.desc(),
                portfolio_briefs.c.id.desc(),
            )
        ).mappings()
        return tuple(
            PortfolioBrief(
                id=row["id"],
                name=row["name"],
                risk_profile=RiskProfile(row["risk_profile"]),
                ai_summary=row["ai_summary"],
                created_at=(
                    row["created_at"].replace(tzinfo=UTC)
                    if row["created_at"].tzinfo is None
                    else row["created_at"]
                ),
            )
            for row in rows
        )

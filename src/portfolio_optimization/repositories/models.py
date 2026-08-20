"""SQLAlchemy persistence models shared by PostgreSQL repositories."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for the application database schema."""


class AssetRow(Base):
    __tablename__ = "assets"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(255))
    currency: Mapped[str] = mapped_column(String(3))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PriceReadingRow(Base):
    __tablename__ = "price_readings"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assets.id", ondelete="CASCADE")
    )
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    close: Mapped[Decimal] = mapped_column(Numeric())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "asset_id", "observed_at", name="uq_reading_asset_time"
        ),
    )


class OptimizationRunRow(Base):
    __tablename__ = "optimization_runs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    method: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16))
    start_date: Mapped[date] = mapped_column(Date())
    end_date: Mapped[date] = mapped_column(Date())
    expected_return: Mapped[Decimal] = mapped_column(Numeric())
    volatility: Mapped[Decimal] = mapped_column(Numeric())
    sharpe_ratio: Mapped[Decimal] = mapped_column(Numeric())
    best_fitness: Mapped[Decimal] = mapped_column(Numeric())
    population_size: Mapped[int] = mapped_column(Integer())
    generations: Mapped[int] = mapped_column(Integer())
    max_weight: Mapped[Decimal] = mapped_column(Numeric())
    diversification_penalty: Mapped[Decimal] = mapped_column(Numeric())
    crossover_rate: Mapped[Decimal] = mapped_column(Numeric())
    mutation_rate: Mapped[Decimal] = mapped_column(Numeric())
    seed: Mapped[int] = mapped_column(Integer())
    convergence_generation: Mapped[int] = mapped_column(Integer())
    runtime_seconds: Mapped[Decimal] = mapped_column(Numeric())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class AllocationRow(Base):
    __tablename__ = "allocations"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    optimization_run_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("optimization_runs.id", ondelete="CASCADE"),
    )
    asset_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("assets.id", ondelete="RESTRICT")
    )
    weight: Mapped[Decimal] = mapped_column(Numeric())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    __table_args__ = (
        UniqueConstraint(
            "optimization_run_id",
            "asset_id",
            name="uq_allocation_run_asset",
        ),
    )


class PortfolioBriefRow(Base):
    __tablename__ = "portfolio_briefs"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    risk_profile: Mapped[str] = mapped_column(String(16))
    ai_summary: Mapped[str] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

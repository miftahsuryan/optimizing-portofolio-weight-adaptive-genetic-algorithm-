"""Create the portfolio optimization schema.

Revision ID: 20260818_0001
Revises: None
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260818_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("symbol", sa.String(32), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("currency = upper(currency)", name="ck_assets_currency_upper"),
        sa.CheckConstraint("symbol = upper(symbol)", name="ck_assets_symbol_upper"),
    )
    op.create_table(
        "optimization_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("method", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("expected_return", sa.Numeric(), nullable=False),
        sa.Column("volatility", sa.Numeric(), nullable=False),
        sa.Column("sharpe_ratio", sa.Numeric(), nullable=False),
        sa.Column("best_fitness", sa.Numeric(), nullable=False),
        sa.Column("population_size", sa.Integer(), nullable=False),
        sa.Column("generations", sa.Integer(), nullable=False),
        sa.Column("max_weight", sa.Numeric(), nullable=False),
        sa.Column("diversification_penalty", sa.Numeric(), nullable=False),
        sa.Column("crossover_rate", sa.Numeric(), nullable=False),
        sa.Column("mutation_rate", sa.Numeric(), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=False),
        sa.Column("convergence_generation", sa.Integer(), nullable=False),
        sa.Column("runtime_seconds", sa.Numeric(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("start_date <= end_date", name="ck_runs_date_range"),
    )
    op.create_table(
        "price_readings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assets.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("close", sa.Numeric(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("close > 0", name="ck_price_readings_close_positive"),
        sa.UniqueConstraint("asset_id", "observed_at", name="uq_reading_asset_time"),
    )
    op.create_index(
        "ix_price_readings_asset_observed_at",
        "price_readings",
        ["asset_id", "observed_at"],
    )
    op.create_table(
        "allocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "optimization_run_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("optimization_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "asset_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assets.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("weight", sa.Numeric(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("weight >= 0 AND weight <= 1", name="ck_allocations_weight"),
        sa.UniqueConstraint(
            "optimization_run_id",
            "asset_id",
            name="uq_allocation_run_asset",
        ),
    )


def downgrade() -> None:
    op.drop_table("allocations")
    op.drop_index("ix_price_readings_asset_observed_at", table_name="price_readings")
    op.drop_table("price_readings")
    op.drop_table("optimization_runs")
    op.drop_table("assets")

"""Add the v0.1 portfolio brief vertical slice.

Revision ID: 20260819_0002
Revises: 20260818_0001
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260819_0002"
down_revision = "20260818_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "portfolio_briefs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("risk_profile", sa.String(16), nullable=False),
        sa.Column("ai_summary", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "risk_profile IN ('conservative', 'balanced', 'growth')",
            name="ck_portfolio_briefs_risk_profile",
        ),
    )
    op.create_index(
        "ix_portfolio_briefs_created_at",
        "portfolio_briefs",
        ["created_at"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_portfolio_briefs_created_at",
        table_name="portfolio_briefs",
    )
    op.drop_table("portfolio_briefs")

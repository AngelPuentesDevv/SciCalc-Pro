"""Agrega columnas status y payload a audit_log.

Revision ID: 002
Revises: 001
Create Date: 2026-04-02
"""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "audit_log",
        sa.Column("status", sa.String(20), nullable=False, server_default="success"),
    )
    op.add_column(
        "audit_log",
        sa.Column("payload", sa.JSON, nullable=True),
    )


def downgrade() -> None:
    op.drop_column("audit_log", "payload")
    op.drop_column("audit_log", "status")

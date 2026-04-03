"""Reemplaza tabla sync_log (mobile/LWW) por audit_log (web-first).

Revision ID: 001
Revises: —
Create Date: 2026-04-02
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = "000"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Eliminar tabla mobile legacy (si existe)
    op.execute("DROP TABLE IF EXISTS sync_log CASCADE")

    # Crear tabla audit_log (web-first)
    op.create_table(
        "audit_log",
        sa.Column("id",          sa.String(36),  primary_key=True),
        sa.Column("user_id",     sa.String(36),  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("entity_type", sa.String(50),  nullable=False),
        sa.Column("entity_id",   sa.String(36),  nullable=False),
        sa.Column("action",      sa.String(20),  nullable=False),
        sa.Column("created_at",  sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_deleted",  sa.Boolean,     nullable=False, server_default="false"),
    )
    op.create_index("ix_audit_log_user_id", "audit_log", ["user_id"])


def downgrade() -> None:
    op.drop_table("audit_log")

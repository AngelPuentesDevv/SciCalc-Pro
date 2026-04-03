"""Renombra device_id → browser_agent en tabla sessions (mobile → web-first).

Revision ID: 003
Revises: 002
Create Date: 2026-04-02
"""
from alembic import op

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("sessions", "device_id", new_column_name="browser_agent")


def downgrade() -> None:
    op.alter_column("sessions", "browser_agent", new_column_name="device_id")

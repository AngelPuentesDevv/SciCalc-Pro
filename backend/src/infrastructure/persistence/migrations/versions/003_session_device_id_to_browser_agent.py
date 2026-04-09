"""Renombra device_id → browser_agent en tabla sessions (mobile → web-first).

Revision ID: 003
Revises: 002
Create Date: 2026-04-02
"""
revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # No-op: migration 000 already creates sessions.browser_agent directly.
    # This migration only applied to pre-existing DBs that had device_id.
    pass


def downgrade() -> None:
    pass

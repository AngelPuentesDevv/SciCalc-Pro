"""Esquema inicial — todas las tablas base del sistema.

Revision ID: 000
Revises: —
Create Date: 2026-04-03
"""
from alembic import op
import sqlalchemy as sa

revision = "000"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── users ─────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id",            sa.String(36),  primary_key=True),
        sa.Column("email",         sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("display_name",  sa.String(100), nullable=False),
        sa.Column("created_at",    sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at",    sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted",    sa.Boolean, nullable=False, server_default="false"),
    )

    # ── profiles ──────────────────────────────────────────────────────────────
    op.create_table(
        "profiles",
        sa.Column("id",                 sa.String(36),  primary_key=True),
        sa.Column("user_id",            sa.String(36),  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("avatar_url",         sa.String(500), nullable=True),
        sa.Column("preferred_precision",sa.Integer,     nullable=True, server_default="10"),
        sa.Column("angle_mode",         sa.String(3),   nullable=True, server_default="DEG"),
        sa.Column("theme",              sa.String(5),   nullable=True, server_default="LIGHT"),
        sa.Column("updated_at",         sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted",         sa.Boolean, nullable=False, server_default="false"),
    )

    # ── calculation_history ───────────────────────────────────────────────────
    op.create_table(
        "calculation_history",
        sa.Column("id",               sa.String(36),  primary_key=True),
        sa.Column("user_id",          sa.String(36),  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("expression",       sa.Text,        nullable=False),
        sa.Column("result",           sa.Text,        nullable=False),
        sa.Column("precision_digits", sa.Integer,     nullable=True, server_default="10"),
        sa.Column("created_at",       sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted",       sa.Boolean, nullable=False, server_default="false"),
        sa.Column("sync_version",     sa.Integer,     nullable=True, server_default="0"),
        sa.Column("device_id",        sa.String(64),  nullable=True),
    )

    # ── user_preferences ──────────────────────────────────────────────────────
    op.create_table(
        "user_preferences",
        sa.Column("id",         sa.String(36),  primary_key=True),
        sa.Column("user_id",    sa.String(36),  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("key",        sa.String(50),  nullable=False),
        sa.Column("value",      sa.String(500), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
    )
    op.create_unique_constraint("uq_user_pref_key", "user_preferences", ["user_id", "key"])

    # ── favorite_conversions ──────────────────────────────────────────────────
    op.create_table(
        "favorite_conversions",
        sa.Column("id",         sa.String(36),  primary_key=True),
        sa.Column("user_id",    sa.String(36),  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("from_unit",  sa.String(30),  nullable=False),
        sa.Column("to_unit",    sa.String(30),  nullable=False),
        sa.Column("category",   sa.String(10),  nullable=False),
        sa.Column("is_deleted", sa.Boolean, nullable=False, server_default="false"),
    )

    # ── sessions ──────────────────────────────────────────────────────────────
    op.create_table(
        "sessions",
        sa.Column("id",             sa.String(36),  primary_key=True),
        sa.Column("user_id",        sa.String(36),  sa.ForeignKey("users.id"), nullable=False),
        sa.Column("browser_agent",  sa.String(255), nullable=False),
        sa.Column("jwt_token_hash", sa.String(255), nullable=False),
        sa.Column("expires_at",     sa.DateTime(timezone=True), nullable=False),
        sa.Column("is_active",      sa.Boolean, nullable=False, server_default="true"),
        sa.Column("is_deleted",     sa.Boolean, nullable=False, server_default="false"),
        sa.Column("created_at",     sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("sessions")
    op.drop_table("favorite_conversions")
    op.drop_constraint("uq_user_pref_key", "user_preferences", type_="unique")
    op.drop_table("user_preferences")
    op.drop_table("calculation_history")
    op.drop_table("profiles")
    op.drop_table("users")

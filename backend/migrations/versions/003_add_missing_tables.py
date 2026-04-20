"""Add missing tables: ip_mappings and task_locations

Revision ID: 003_add_missing_tables
Revises: 002_add_missing_columns
Create Date: 2026-04-13 19:15:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

revision = "003_add_missing_tables"
down_revision = "002_add_missing_columns"
branch_labels = None
depends_on = None


def _table_exists(table_name: str) -> bool:
    """Check if a table already exists in the database."""
    bind = op.get_bind()
    inspector = inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    # Create ip_mappings table (skip if exists)
    if not _table_exists("ip_mappings"):
        op.create_table(
            "ip_mappings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("ip_pattern", sa.String(100), nullable=False),
            sa.Column("category", sa.String(50), nullable=False),
            sa.Column(
                "auto", sa.Boolean(), nullable=False, server_default=sa.text("true")
            ),
            sa.Column(
                "manual_override",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("false"),
            ),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.Column("updated_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("ip_pattern"),
        )

    # Create task_locations table (skip if exists)
    if not _table_exists("task_locations"):
        op.create_table(
            "task_locations",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column(
                "task_id",
                sa.Integer(),
                sa.ForeignKey("tasks.id", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("ip", sa.String(100), nullable=False),
            sa.Column("location", sa.Text(), nullable=True),
            sa.Column("category", sa.String(50), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    if _table_exists("task_locations"):
        op.drop_table("task_locations")
    if _table_exists("ip_mappings"):
        op.drop_table("ip_mappings")

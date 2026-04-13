"""Add missing tables: ip_mappings and task_locations

Revision ID: 003_add_missing_tables
Revises: 002_add_missing_columns
Create Date: 2026-04-13 19:15:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "003_add_missing_tables"
down_revision = "002_add_missing_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ip_mappings table
    op.create_table(
        "ip_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ip_pattern", sa.String(100), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("auto", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("manual_override", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ip_pattern"),
    )

    # Create task_locations table
    op.create_table(
        "task_locations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), sa.ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("ip", sa.String(100), nullable=False),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("task_locations")
    op.drop_table("ip_mappings")

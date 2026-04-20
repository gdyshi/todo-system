"""Add missing columns to tasks table

Revision ID: 002_add_missing_columns
Revises: 001_initial
Create Date: 2026-04-13 18:45:00.000000

"""

from alembic import op
import sqlalchemy as sa

revision = "002_add_missing_columns"
down_revision = "001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add parent_id column
    op.add_column(
        "tasks",
        sa.Column(
            "parent_id",
            sa.Integer(),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    # Change priority from String to Integer
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.String(),
        type_=sa.Integer(),
        nullable=True,
    )
    # Add due_time column
    op.add_column("tasks", sa.Column("due_time", sa.DateTime(), nullable=True))
    # Add location column
    op.add_column("tasks", sa.Column("location", sa.Text(), nullable=True))
    # Add reminder_sent column
    op.add_column("tasks", sa.Column("reminder_sent", sa.Boolean(), nullable=True))
    # Change description from String to Text
    op.alter_column(
        "tasks",
        "description",
        existing_type=sa.String(),
        type_=sa.Text(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "tasks",
        "description",
        existing_type=sa.Text(),
        type_=sa.String(),
        nullable=True,
    )
    op.drop_column("tasks", "reminder_sent")
    op.drop_column("tasks", "location")
    op.drop_column("tasks", "due_time")
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.Integer(),
        type_=sa.String(),
        nullable=True,
    )
    op.drop_column("tasks", "parent_id")

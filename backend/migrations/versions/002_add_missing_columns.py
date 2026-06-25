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
    # Add parent_id column (IF NOT EXISTS via raw SQL)
    op.execute("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS parent_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE
        """)
    # Change priority from String to Integer (idempotent: no-op if already Integer)
    op.execute(
        "ALTER TABLE tasks ALTER COLUMN priority TYPE INTEGER USING priority::INTEGER"
    )
    # Add due_time column
    op.execute("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS due_time TIMESTAMP
        """)
    # Add location column
    op.execute("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS location TEXT
        """)
    # Add reminder_sent column
    op.execute("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN
        """)
    # Change description from String to Text (idempotent: no-op if already Text)
    op.execute("ALTER TABLE tasks ALTER COLUMN description TYPE TEXT")


def downgrade() -> None:
    op.execute("ALTER TABLE tasks ALTER COLUMN description TYPE VARCHAR")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS reminder_sent")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS location")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS due_time")
    op.execute("ALTER TABLE tasks ALTER COLUMN priority TYPE VARCHAR")
    op.execute("ALTER TABLE tasks DROP COLUMN IF EXISTS parent_id")

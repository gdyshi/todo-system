"""Initial migration - Create base tables

Revision ID: 001_initial
Revises:
Create Date: 2026-03-28 17:44:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Use raw SQL with IF NOT EXISTS to support databases where tables already exist
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER NOT NULL,
            title VARCHAR NOT NULL,
            description VARCHAR,
            category VARCHAR,
            status VARCHAR NOT NULL,
            priority VARCHAR,
            created_at TIMESTAMP NOT NULL,
            updated_at TIMESTAMP NOT NULL,
            PRIMARY KEY (id)
        )
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS ix_tasks_category ON tasks (category)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_tasks_status ON tasks (status)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS tasks")

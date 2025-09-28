"""Add profile preference fields"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240927_0004'
down_revision = '20240611_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('preferred_branch', sa.String(length=160), nullable=True))
    op.add_column('users', sa.Column('motivation', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'motivation')
    op.drop_column('users', 'preferred_branch')

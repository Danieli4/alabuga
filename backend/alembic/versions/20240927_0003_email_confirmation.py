"""Add email confirmation fields to users"""

from __future__ import annotations

from datetime import datetime

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240927_0003'
down_revision = '20240611_0002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('users', sa.Column('is_email_confirmed', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column('users', sa.Column('email_confirmation_token', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('email_confirmed_at', sa.DateTime(timezone=True), nullable=True))
    op.execute('UPDATE users SET is_email_confirmed = 1')
    op.alter_column('users', 'is_email_confirmed', server_default=None)


def downgrade() -> None:
    op.drop_column('users', 'email_confirmed_at')
    op.drop_column('users', 'email_confirmation_token')
    op.drop_column('users', 'is_email_confirmed')

"""Add submission document fields"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240927_0005'
down_revision = '20240927_0004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('mission_submissions', sa.Column('passport_path', sa.String(length=512), nullable=True))
    op.add_column('mission_submissions', sa.Column('photo_path', sa.String(length=512), nullable=True))
    op.add_column('mission_submissions', sa.Column('resume_path', sa.String(length=512), nullable=True))
    op.add_column('mission_submissions', sa.Column('resume_link', sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column('mission_submissions', 'resume_link')
    op.drop_column('mission_submissions', 'resume_path')
    op.drop_column('mission_submissions', 'photo_path')
    op.drop_column('mission_submissions', 'passport_path')

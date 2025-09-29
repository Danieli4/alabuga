"""Add python mission tables"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '20240927_0007'
down_revision = '20240927_0006'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'python_challenges',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('mission_id', sa.Integer(), sa.ForeignKey('missions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('input_data', sa.Text(), nullable=True),
        sa.Column('expected_output', sa.Text(), nullable=False),
        sa.Column('starter_code', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint('mission_id', 'order', name='uq_python_challenge_mission_order'),
    )

    op.create_table(
        'python_user_progress',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('mission_id', sa.Integer(), sa.ForeignKey('missions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('current_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'mission_id', name='uq_python_progress_user_mission'),
    )

    op.create_table(
        'python_submissions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('progress_id', sa.Integer(), sa.ForeignKey('python_user_progress.id', ondelete='CASCADE'), nullable=False),
        sa.Column('challenge_id', sa.Integer(), sa.ForeignKey('python_challenges.id', ondelete='CASCADE'), nullable=False),
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('stdout', sa.Text(), nullable=True),
        sa.Column('stderr', sa.Text(), nullable=True),
        sa.Column('is_passed', sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index('ix_python_submissions_progress_id', 'python_submissions', ['progress_id'])
    op.create_index('ix_python_submissions_challenge_id', 'python_submissions', ['challenge_id'])


def downgrade() -> None:
    op.drop_index('ix_python_submissions_challenge_id', table_name='python_submissions')
    op.drop_index('ix_python_submissions_progress_id', table_name='python_submissions')
    op.drop_table('python_submissions')
    op.drop_table('python_user_progress')
    op.drop_table('python_challenges')

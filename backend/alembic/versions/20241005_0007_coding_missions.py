"""Добавляем таблицы для кодовых миссий."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20241005_0007"
down_revision = "20240927_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Создаём таблицы испытаний и попыток запуска кода."""

    op.create_table(
        "coding_challenges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id"), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("prompt", sa.Text(), nullable=False),
        sa.Column("starter_code", sa.Text(), nullable=True),
        sa.Column("expected_output", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("mission_id", "order", name="uq_coding_challenge_order"),
    )

    op.create_table(
        "coding_attempts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("challenge_id", sa.Integer(), sa.ForeignKey("coding_challenges.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("stdout", sa.Text(), nullable=False, server_default=""),
        sa.Column("stderr", sa.Text(), nullable=False, server_default=""),
        sa.Column("exit_code", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_passed", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_index(
        "ix_coding_challenges_mission_id",
        "coding_challenges",
        ["mission_id"],
        unique=False,
    )
    op.create_index(
        "ix_coding_attempts_user_id",
        "coding_attempts",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Удаляем вспомогательные таблицы."""

    op.drop_index("ix_coding_attempts_user_id", table_name="coding_attempts")
    op.drop_index("ix_coding_challenges_mission_id", table_name="coding_challenges")
    op.drop_table("coding_attempts")
    op.drop_table("coding_challenges")


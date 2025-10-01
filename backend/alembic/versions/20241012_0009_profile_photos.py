"""Добавляем колонку для фото профиля кандидата."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20241012_0009"
down_revision = "20241010_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(sa.Column("profile_photo_path", sa.String(length=512), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("profile_photo_path")

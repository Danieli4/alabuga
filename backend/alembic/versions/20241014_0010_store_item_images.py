"""Add image url to store items"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20241014_0010"
down_revision = "20241012_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Добавляем колонку с изображением товара."""

    op.add_column("store_items", sa.Column("image_url", sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Удаляем колонку с изображением товара."""

    op.drop_column("store_items", "image_url")

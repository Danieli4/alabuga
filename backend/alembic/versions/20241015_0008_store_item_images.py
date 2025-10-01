"""Add image path to store items"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "20241015_0008"
down_revision = "3c5430b2cbd3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("store_items", sa.Column("image_url", sa.String(length=512), nullable=True))


def downgrade() -> None:
    op.drop_column("store_items", "image_url")

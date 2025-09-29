"""Merge heads: python and coding mission branches."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "3c5430b2cbd3"
down_revision = ("20240927_0007", "20241005_0007")
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass


def downgrade() -> None:
    pass

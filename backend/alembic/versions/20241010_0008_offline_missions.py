"""offline missions fields

Revision ID: 20241010_0008
Revises: 3c5430b2cbd3
Create Date: 2024-10-10 00:08:00.000000
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20241010_0008"
down_revision = "3c5430b2cbd3"
branch_labels = None
depends_on = None


mission_format_enum = sa.Enum("online", "offline", name="missionformat")

def upgrade() -> None:
    mission_format_enum.create(op.get_bind(), checkfirst=True)
    with op.batch_alter_table("missions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("format", mission_format_enum, nullable=False, server_default="online"))
        batch_op.add_column(sa.Column("event_location", sa.String(length=160), nullable=True))
        batch_op.add_column(sa.Column("event_address", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("event_starts_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("event_ends_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("registration_deadline", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("registration_url", sa.String(length=512), nullable=True))
        batch_op.add_column(sa.Column("registration_notes", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("capacity", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("contact_person", sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column("contact_phone", sa.String(length=64), nullable=True))
    op.execute("UPDATE missions SET format = 'online' WHERE format IS NULL")
    with op.batch_alter_table("missions", schema=None) as batch_op:
        batch_op.alter_column("format", server_default=None)


def downgrade() -> None:
    with op.batch_alter_table("missions", schema=None) as batch_op:
        batch_op.drop_column("contact_phone")
        batch_op.drop_column("contact_person")
        batch_op.drop_column("capacity")
        batch_op.drop_column("registration_notes")
        batch_op.drop_column("registration_url")
        batch_op.drop_column("registration_deadline")
        batch_op.drop_column("event_ends_at")
        batch_op.drop_column("event_starts_at")
        batch_op.drop_column("event_address")
        batch_op.drop_column("event_location")
        batch_op.drop_column("format")
    mission_format_enum.drop(op.get_bind(), checkfirst=True)

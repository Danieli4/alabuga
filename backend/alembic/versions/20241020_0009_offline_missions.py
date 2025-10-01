"""Add offline mission support"""

from __future__ import annotations
"""Add offline mission support."""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "20241020_0009"
down_revision = "20241015_0008"
branch_labels = None
depends_on = None


MISSION_FORMAT_ENUM = sa.Enum(
    "online", "offline", name="missionformat", native_enum=False
)


def upgrade() -> None:
    op.add_column(
        "missions",
        sa.Column(
            "format",
            MISSION_FORMAT_ENUM,
            nullable=False,
            server_default="online",
        ),
    )
    op.add_column(
        "missions",
        sa.Column("registration_deadline", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("location_title", sa.String(length=160), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("location_address", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("location_url", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "missions",
        sa.Column("capacity", sa.Integer(), nullable=True),
    )

    op.create_table(
        "mission_registrations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("mission_id", "user_id", name="uq_mission_registration"),
    )
    op.create_index(
        "ix_mission_registrations_mission_id",
        "mission_registrations",
        ["mission_id"],
    )
    op.create_index(
        "ix_mission_registrations_user_id",
        "mission_registrations",
        ["user_id"],
    )

    op.execute("UPDATE missions SET format='online' WHERE format IS NULL")
    bind = op.get_bind()
    if bind.dialect.name != "sqlite":
        op.alter_column("missions", "format", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_mission_registrations_user_id", table_name="mission_registrations")
    op.drop_index("ix_mission_registrations_mission_id", table_name="mission_registrations")
    op.drop_table("mission_registrations")

    op.drop_column("missions", "capacity")
    op.drop_column("missions", "location_url")
    op.drop_column("missions", "location_address")
    op.drop_column("missions", "location_title")
    op.drop_column("missions", "ends_at")
    op.drop_column("missions", "starts_at")
    op.drop_column("missions", "registration_deadline")
    op.drop_column("missions", "format")

    MISSION_FORMAT_ENUM.drop(op.get_bind(), checkfirst=False)

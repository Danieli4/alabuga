"""Onboarding models"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20240611_0002"
down_revision = "20240609_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "onboarding_slides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("media_url", sa.String(length=512)),
        sa.Column("cta_text", sa.String(length=120)),
        sa.Column("cta_link", sa.String(length=512)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("order", name="uq_onboarding_slide_order"),
    )

    op.create_table(
        "onboarding_states",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("last_completed_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.sql.expression.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            server_onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", name="uq_onboarding_state_user"),
    )


def downgrade() -> None:
    op.drop_table("onboarding_states")
    op.drop_table("onboarding_slides")


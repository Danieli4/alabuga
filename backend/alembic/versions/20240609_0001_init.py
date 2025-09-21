"""initial schema"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "20240609_0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    user_role = sa.Enum("pilot", "hr", "admin", name="userrole")
    competency_category = sa.Enum(
        "communication", "analytics", "teamwork", "leadership", "technology", "culture", name="competencycategory"
    )
    artifact_rarity = sa.Enum("common", "rare", "epic", "legendary", name="artifactrarity")
    mission_difficulty = sa.Enum("easy", "medium", "hard", name="missiondifficulty")
    submission_status = sa.Enum("pending", "approved", "rejected", name="submissionstatus")
    order_status = sa.Enum("created", "approved", "rejected", "delivered", name="orderstatus")
    journal_event = sa.Enum(
        "rank_up", "mission_completed", "order_created", "order_approved", "skill_up", name="journaleventtype"
    )

    op.create_table(
        "ranks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=120), nullable=False, unique=True),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("required_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "competencies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False, unique=True),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("category", competency_category, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("rarity", artifact_rarity, nullable=False),
        sa.Column("image_url", sa.String(length=512)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="pilot"),
        sa.Column("xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mana", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_rank_id", sa.Integer(), sa.ForeignKey("ranks.id")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "user_competencies",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("competency_id", sa.Integer(), sa.ForeignKey("competencies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "competency_id", name="uq_user_competency"),
    )

    op.create_table(
        "user_artifacts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("artifact_id", sa.Integer(), sa.ForeignKey("artifacts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "artifact_id", name="uq_user_artifact"),
    )

    op.create_table(
        "branches",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=120), nullable=False, unique=True),
        sa.Column("description", sa.String(length=512), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False, server_default="quest"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "missions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("xp_reward", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mana_reward", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("difficulty", mission_difficulty, nullable=False, server_default="medium"),
        sa.Column("minimum_rank_id", sa.Integer(), sa.ForeignKey("ranks.id")),
        sa.Column("artifact_id", sa.Integer(), sa.ForeignKey("artifacts.id")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.sql.expression.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "branch_missions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("branch_id", sa.Integer(), sa.ForeignKey("branches.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "mission_competency_rewards",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("competency_id", sa.Integer(), sa.ForeignKey("competencies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level_delta", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("mission_id", "competency_id", name="uq_mission_competency"),
    )

    op.create_table(
        "mission_prerequisites",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "required_mission_id",
            sa.Integer(),
            sa.ForeignKey("missions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("mission_id", "required_mission_id", name="uq_mission_prerequisite"),
    )

    op.create_table(
        "rank_mission_requirements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rank_id", sa.Integer(), sa.ForeignKey("ranks.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("rank_id", "mission_id", name="uq_rank_mission"),
    )

    op.create_table(
        "rank_competency_requirements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rank_id", sa.Integer(), sa.ForeignKey("ranks.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "competency_id", sa.Integer(), sa.ForeignKey("competencies.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("required_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("rank_id", "competency_id", name="uq_rank_competency"),
    )

    op.create_table(
        "mission_submissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mission_id", sa.Integer(), sa.ForeignKey("missions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", submission_status, nullable=False, server_default="pending"),
        sa.Column("comment", sa.Text()),
        sa.Column("proof_url", sa.String(length=512)),
        sa.Column("awarded_xp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("awarded_mana", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("user_id", "mission_id", name="uq_user_mission_submission"),
    )

    op.create_table(
        "store_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("cost_mana", sa.Integer(), nullable=False),
        sa.Column("stock", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("store_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("status", order_status, nullable=False, server_default="created"),
        sa.Column("comment", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )

    op.create_table(
        "journal_entries",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", journal_event, nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("payload", sa.JSON()),
        sa.Column("xp_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("mana_delta", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), server_onupdate=sa.func.now(), nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table("journal_entries")
    op.drop_table("orders")
    op.drop_table("store_items")
    op.drop_table("mission_submissions")
    op.drop_table("rank_competency_requirements")
    op.drop_table("rank_mission_requirements")
    op.drop_table("mission_prerequisites")
    op.drop_table("mission_competency_rewards")
    op.drop_table("branch_missions")
    op.drop_table("missions")
    op.drop_table("branches")
    op.drop_table("user_artifacts")
    op.drop_table("user_competencies")
    op.drop_table("users")
    op.drop_table("artifacts")
    op.drop_table("competencies")
    op.drop_table("ranks")
    sa.Enum(name="journaleventtype").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="orderstatus").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="submissionstatus").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="missiondifficulty").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="artifactrarity").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="competencycategory").drop(op.get_bind(), checkfirst=False)
    sa.Enum(name="userrole").drop(op.get_bind(), checkfirst=False)

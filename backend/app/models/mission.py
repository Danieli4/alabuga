"""Миссии, требования и отправки отчётов."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.coding import CodingChallenge


class MissionDifficulty(str, Enum):
    """Условные уровни сложности."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MissionFormat(str, Enum):
    """Формат проведения миссии."""

    ONLINE = "online"
    OFFLINE = "offline"


class Mission(Base, TimestampMixin):
    """Игровая миссия."""

    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    xp_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mana_reward: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    difficulty: Mapped[MissionDifficulty] = mapped_column(
        SQLEnum(MissionDifficulty), default=MissionDifficulty.MEDIUM, nullable=False
    )
    format: Mapped[MissionFormat] = mapped_column(
        SQLEnum(MissionFormat), default=MissionFormat.ONLINE, nullable=False
    )
    event_location: Mapped[Optional[str]] = mapped_column(String(160))
    event_address: Mapped[Optional[str]] = mapped_column(String(255))
    event_starts_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    event_ends_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    registration_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    registration_url: Mapped[Optional[str]] = mapped_column(String(512))
    registration_notes: Mapped[Optional[str]] = mapped_column(Text)
    capacity: Mapped[Optional[int]] = mapped_column(Integer)
    contact_person: Mapped[Optional[str]] = mapped_column(String(120))
    contact_phone: Mapped[Optional[str]] = mapped_column(String(64))
    minimum_rank_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ranks.id"))
    artifact_id: Mapped[Optional[int]] = mapped_column(ForeignKey("artifacts.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    minimum_rank = relationship("Rank")
    artifact = relationship("Artifact", back_populates="missions")
    branches: Mapped[List["BranchMission"]] = relationship("BranchMission", back_populates="mission")
    competency_rewards: Mapped[List["MissionCompetencyReward"]] = relationship(
        "MissionCompetencyReward", back_populates="mission", cascade="all, delete-orphan"
    )
    prerequisites: Mapped[List["MissionPrerequisite"]] = relationship(
        "MissionPrerequisite", foreign_keys="MissionPrerequisite.mission_id", back_populates="mission"
    )
    required_for: Mapped[List["MissionPrerequisite"]] = relationship(
        "MissionPrerequisite",
        foreign_keys="MissionPrerequisite.required_mission_id",
        back_populates="required_mission",
    )
    submissions: Mapped[List["MissionSubmission"]] = relationship(
        "MissionSubmission", back_populates="mission", cascade="all, delete-orphan"
    )
    rank_requirements: Mapped[List["RankMissionRequirement"]] = relationship(
        "RankMissionRequirement", back_populates="mission"
    )
    coding_challenges: Mapped[List["CodingChallenge"]] = relationship(
        "CodingChallenge",
        back_populates="mission",
        cascade="all, delete-orphan",
        order_by="CodingChallenge.order",
    )


class MissionCompetencyReward(Base, TimestampMixin):
    """Какие компетенции повышаются за миссию."""

    __tablename__ = "mission_competency_rewards"
    __table_args__ = (UniqueConstraint("mission_id", "competency_id", name="uq_mission_competency"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)
    competency_id: Mapped[int] = mapped_column(ForeignKey("competencies.id"), nullable=False)
    level_delta: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    mission = relationship("Mission", back_populates="competency_rewards")
    competency = relationship("Competency")


class MissionPrerequisite(Base, TimestampMixin):
    """Связка миссий с зависимостями."""

    __tablename__ = "mission_prerequisites"
    __table_args__ = (
        UniqueConstraint("mission_id", "required_mission_id", name="uq_mission_prerequisite"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)
    required_mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)

    mission = relationship(
        "Mission", foreign_keys=[mission_id], back_populates="prerequisites"
    )
    required_mission = relationship(
        "Mission", foreign_keys=[required_mission_id], back_populates="required_for"
    )


class SubmissionStatus(str, Enum):
    """Статусы проверки отправленных заданий."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MissionSubmission(Base, TimestampMixin):
    """Отправка выполненной миссии пользователем."""

    __tablename__ = "mission_submissions"
    __table_args__ = (
        UniqueConstraint("user_id", "mission_id", name="uq_user_mission_submission"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)
    status: Mapped[SubmissionStatus] = mapped_column(
        SQLEnum(SubmissionStatus), default=SubmissionStatus.PENDING, nullable=False
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proof_url: Mapped[Optional[str]] = mapped_column(String(512))
    passport_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    photo_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    resume_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    resume_link: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    awarded_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    awarded_mana: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    mission = relationship("Mission", back_populates="submissions")
    user = relationship("User", back_populates="submissions")

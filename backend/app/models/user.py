"""Модели пользователей и связанных сущностей."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

# Локальные импорты внизу файла, чтобы избежать циклов типов


class UserRole(str, Enum):
    """Типы ролей в системе."""

    PILOT = "pilot"
    HR = "hr"
    ADMIN = "admin"


class User(Base, TimestampMixin):
    """Пользователь платформы."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.PILOT, index=True)
    xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mana: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_rank_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ranks.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_email_confirmed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    email_confirmation_token: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    email_confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    # Храним пожелания кандидата: в какой ветке развития он хочет расти.
    preferred_branch: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    # Короткая заметка с личной мотивацией — помогает HR при первичном контакте.
    motivation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    current_rank = relationship("Rank", back_populates="pilots")
    competencies: Mapped[List["UserCompetency"]] = relationship(
        "UserCompetency", back_populates="user", cascade="all, delete-orphan"
    )
    submissions: Mapped[List["MissionSubmission"]] = relationship(
        "MissionSubmission", back_populates="user", cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="user")
    journal_entries: Mapped[List["JournalEntry"]] = relationship(
        "JournalEntry", back_populates="user", cascade="all, delete-orphan"
    )
    artifacts: Mapped[List["UserArtifact"]] = relationship(
        "UserArtifact", back_populates="user", cascade="all, delete-orphan"
    )
    onboarding_state: Mapped[Optional["OnboardingState"]] = relationship(
        "OnboardingState", back_populates="user", cascade="all, delete-orphan", uselist=False
    )


class CompetencyCategory(str, Enum):
    """Категории компетенций."""

    COMMUNICATION = "communication"
    ANALYTICS = "analytics"
    TEAMWORK = "teamwork"
    LEADERSHIP = "leadership"
    TECH = "technology"
    CULTURE = "culture"


class Competency(Base, TimestampMixin):
    """Компетенция с уровнем прокачки."""

    __tablename__ = "competencies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    category: Mapped[CompetencyCategory] = mapped_column(
        SQLEnum(CompetencyCategory), nullable=False, index=True
    )

    users: Mapped[List["UserCompetency"]] = relationship("UserCompetency", back_populates="competency")


class UserCompetency(Base, TimestampMixin):
    """Уровень компетенции для конкретного пользователя."""

    __tablename__ = "user_competencies"
    __table_args__ = (UniqueConstraint("user_id", "competency_id", name="uq_user_competency"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    competency_id: Mapped[int] = mapped_column(ForeignKey("competencies.id"), nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="competencies")
    competency = relationship("Competency", back_populates="users")


class UserArtifact(Base, TimestampMixin):
    """Коллекция артефактов пользователя."""

    __tablename__ = "user_artifacts"
    __table_args__ = (UniqueConstraint("user_id", "artifact_id", name="uq_user_artifact"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    artifact_id: Mapped[int] = mapped_column(ForeignKey("artifacts.id"), nullable=False)

    user = relationship("User", back_populates="artifacts")
    artifact = relationship("Artifact", back_populates="pilots")


# Импорты в конце файла, чтобы отношения корректно инициализировались
from app.models.onboarding import OnboardingState  # noqa: E402  pylint: disable=wrong-import-position

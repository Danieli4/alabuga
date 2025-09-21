"""Модели рангов и условий повышения."""

from __future__ import annotations

from typing import List

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Rank(Base, TimestampMixin):
    """Игровой ранг."""

    __tablename__ = "ranks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    required_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    pilots: Mapped[List["User"]] = relationship("User", back_populates="current_rank")
    mission_requirements: Mapped[List["RankMissionRequirement"]] = relationship(
        "RankMissionRequirement", back_populates="rank", cascade="all, delete-orphan"
    )
    competency_requirements: Mapped[List["RankCompetencyRequirement"]] = relationship(
        "RankCompetencyRequirement", back_populates="rank", cascade="all, delete-orphan"
    )


class RankMissionRequirement(Base, TimestampMixin):
    """Связка ранга и обязательных миссий."""

    __tablename__ = "rank_mission_requirements"
    __table_args__ = (UniqueConstraint("rank_id", "mission_id", name="uq_rank_mission"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    rank_id: Mapped[int] = mapped_column(ForeignKey("ranks.id"), nullable=False)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)

    rank = relationship("Rank", back_populates="mission_requirements")
    mission = relationship("Mission", back_populates="rank_requirements")


class RankCompetencyRequirement(Base, TimestampMixin):
    """Требования к прокачке компетенций."""

    __tablename__ = "rank_competency_requirements"
    __table_args__ = (UniqueConstraint("rank_id", "competency_id", name="uq_rank_competency"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    rank_id: Mapped[int] = mapped_column(ForeignKey("ranks.id"), nullable=False)
    competency_id: Mapped[int] = mapped_column(ForeignKey("competencies.id"), nullable=False)
    required_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    rank = relationship("Rank", back_populates="competency_requirements")
    competency = relationship("Competency")

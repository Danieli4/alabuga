"""Ветки миссий и их порядок."""

from __future__ import annotations

from typing import List

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Branch(Base, TimestampMixin):
    """Объединение миссий в сюжетную ветку."""

    __tablename__ = "branches"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(512), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, default="quest")

    missions: Mapped[List["BranchMission"]] = relationship(
        "BranchMission", back_populates="branch", cascade="all, delete-orphan"
    )


class BranchMission(Base, TimestampMixin):
    """Связка ветки и миссии с порядком."""

    __tablename__ = "branch_missions"

    id: Mapped[int] = mapped_column(primary_key=True)
    branch_id: Mapped[int] = mapped_column(ForeignKey("branches.id"), nullable=False)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    branch = relationship("Branch", back_populates="missions")
    mission = relationship("Mission", back_populates="branches")

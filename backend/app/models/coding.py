"""Модели для кодовых испытаний внутри миссий."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class CodingChallenge(Base, TimestampMixin):
    """Шаг миссии с заданием на программирование."""

    __tablename__ = "coding_challenges"
    __table_args__ = (
        # Порядок внутри миссии должен быть уникальным, чтобы упрощать проверку последовательности.
        UniqueConstraint("mission_id", "order", name="uq_coding_challenge_order"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id"), nullable=False, index=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)

    mission = relationship("Mission", back_populates="coding_challenges")
    attempts: Mapped[List["CodingAttempt"]] = relationship(
        "CodingAttempt", back_populates="challenge", cascade="all, delete-orphan"
    )


class CodingAttempt(Base, TimestampMixin):
    """История запусков кода пилота для конкретного задания."""

    __tablename__ = "coding_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("coding_challenges.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    stdout: Mapped[str] = mapped_column(Text, nullable=False, default="")
    stderr: Mapped[str] = mapped_column(Text, nullable=False, default="")
    exit_code: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    challenge = relationship("CodingChallenge", back_populates="attempts")
    user = relationship("User", back_populates="coding_attempts")


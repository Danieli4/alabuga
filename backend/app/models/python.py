"""Модели миссии по Python и пользовательского прогресса."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class PythonChallenge(Base, TimestampMixin):
    """Задание в рамках миссии "Основы Python"."""

    __tablename__ = "python_challenges"

    id: Mapped[int] = mapped_column(primary_key=True)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    input_data: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_output: Mapped[str] = mapped_column(Text, nullable=False)
    starter_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    submissions: Mapped[list["PythonSubmission"]] = relationship("PythonSubmission", back_populates="challenge")


class PythonUserProgress(Base, TimestampMixin):
    """Прогресс пользователя по задачам Python-миссии."""

    __tablename__ = "python_user_progress"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    mission_id: Mapped[int] = mapped_column(ForeignKey("missions.id", ondelete="CASCADE"), nullable=False)
    current_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    submissions: Mapped[list["PythonSubmission"]] = relationship("PythonSubmission", back_populates="progress")


class PythonSubmission(Base, TimestampMixin):
    """Хранение попыток решения конкретной задачи."""

    __tablename__ = "python_submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    progress_id: Mapped[int] = mapped_column(ForeignKey("python_user_progress.id", ondelete="CASCADE"), nullable=False)
    challenge_id: Mapped[int] = mapped_column(ForeignKey("python_challenges.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(Text, nullable=False)
    stdout: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stderr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_passed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    progress: Mapped[PythonUserProgress] = relationship("PythonUserProgress", back_populates="submissions")
    challenge: Mapped[PythonChallenge] = relationship("PythonChallenge", back_populates="submissions")

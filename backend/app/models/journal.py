"""Бортовой журнал событий."""

from __future__ import annotations

from enum import Enum

from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class JournalEventType(str, Enum):
    """Типы событий для журнала."""

    RANK_UP = "rank_up"
    MISSION_COMPLETED = "mission_completed"
    ORDER_CREATED = "order_created"
    ORDER_APPROVED = "order_approved"
    SKILL_UP = "skill_up"


class JournalEntry(Base, TimestampMixin):
    """Запись о важном событии пользователя."""

    __tablename__ = "journal_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    event_type: Mapped[JournalEventType] = mapped_column(SQLEnum(JournalEventType), nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSON)
    xp_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    mana_delta: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user = relationship("User", back_populates="journal_entries")

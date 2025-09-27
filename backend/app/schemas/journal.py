"""Схемы бортового журнала."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.journal import JournalEventType


class JournalEntryRead(BaseModel):
    """Запись журнала."""

    id: int
    event_type: JournalEventType
    title: str
    description: str
    payload: Optional[dict]
    xp_delta: int
    mana_delta: int
    created_at: datetime

    class Config:
        from_attributes = True


class LeaderboardEntry(BaseModel):
    """Участник таблицы лидеров."""

    user_id: int
    full_name: str
    xp_delta: int
    mana_delta: int


class LeaderboardResponse(BaseModel):
    """Ответ для таблицы лидеров."""

    period: str
    entries: list[LeaderboardEntry]

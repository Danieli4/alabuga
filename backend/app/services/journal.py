"""Сервисные функции для журнала."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.journal import JournalEntry, JournalEventType


def log_event(
    db: Session,
    *,
    user_id: int,
    event_type: JournalEventType,
    title: str,
    description: str,
    payload: dict | None = None,
    xp_delta: int = 0,
    mana_delta: int = 0,
) -> JournalEntry:
    """Создаём запись журнала и возвращаем её."""

    entry = JournalEntry(
        user_id=user_id,
        event_type=event_type,
        title=title,
        description=description,
        payload=payload,
        xp_delta=xp_delta,
        mana_delta=mana_delta,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

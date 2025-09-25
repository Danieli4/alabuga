"""Чтение журнала событий."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.journal import JournalEntry
from app.models.user import User
from app.schemas.journal import JournalEntryRead, LeaderboardEntry, LeaderboardResponse

router = APIRouter(prefix="/api/journal", tags=["journal"])


@router.get("/", response_model=list[JournalEntryRead], summary="Журнал пользователя")
def list_journal(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[JournalEntryRead]:
    """Возвращаем записи, отсортированные по времени."""

    entries = (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
        .all()
    )
    return [JournalEntryRead.model_validate(entry) for entry in entries]


@router.get("/leaderboard", response_model=LeaderboardResponse, summary="Таблица лидеров")
def leaderboard(
    period: str = "week",
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeaderboardResponse:
    """Возвращаем топ пилотов по опыту и мане за выбранный период."""

    del current_user  # информация используется только для авторизации

    periods = {"week": 7, "month": 30, "year": 365}
    if period not in periods:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неизвестный период")

    since = datetime.now(timezone.utc) - timedelta(days=periods[period])

    rows = (
        db.query(
            User.id.label("user_id"),
            User.full_name,
            func.sum(JournalEntry.xp_delta).label("xp_sum"),
            func.sum(JournalEntry.mana_delta).label("mana_sum"),
        )
        .join(User, User.id == JournalEntry.user_id)
        .filter(JournalEntry.created_at >= since)
        .group_by(User.id, User.full_name)
        .order_by(func.sum(JournalEntry.xp_delta).desc())
        .limit(5)
        .all()
    )

    entries = [
        LeaderboardEntry(
            user_id=row.user_id,
            full_name=row.full_name,
            xp_delta=int(row.xp_sum or 0),
            mana_delta=int(row.mana_sum or 0),
        )
        for row in rows
    ]

    return LeaderboardResponse(period=period, entries=entries)

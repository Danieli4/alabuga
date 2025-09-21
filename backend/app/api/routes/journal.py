"""Чтение журнала событий."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.journal import JournalEntry
from app.models.user import User
from app.schemas.journal import JournalEntryRead

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

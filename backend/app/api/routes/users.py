"""Маршруты работы с профилем."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import UserProfile

router = APIRouter(prefix="/api", tags=["profile"])


@router.get("/me", response_model=UserProfile, summary="Профиль пилота")
def get_profile(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> UserProfile:
    """Возвращаем профиль и связанные сущности."""

    db.refresh(current_user)
    _ = current_user.competencies
    _ = current_user.artifacts
    return UserProfile.model_validate(current_user)

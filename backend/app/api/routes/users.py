"""Маршруты работы с профилем."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.rank import Rank
from app.models.user import User
from app.schemas.rank import RankBase
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


@router.get("/ranks", response_model=list[RankBase], summary="Перечень рангов")
def list_ranks(
    *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[RankBase]:
    """Возвращаем ранги по возрастанию требований."""

    ranks = db.query(Rank).order_by(Rank.required_xp).all()
    return [RankBase.model_validate(rank) for rank in ranks]

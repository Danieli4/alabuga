"""Онбординг и космический лор."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.onboarding import (
    OnboardingCompleteRequest,
    OnboardingOverview,
    OnboardingSlideRead,
    OnboardingStateRead,
)
from app.services.onboarding import complete_slide, get_overview


router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


@router.get("/", response_model=OnboardingOverview, summary="Лор и прогресс онбординга")
def read_onboarding(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OnboardingOverview:
    """Отдаём все слайды вместе с состоянием пользователя."""

    slides, state, next_order = get_overview(db, current_user)
    return OnboardingOverview(
        slides=[OnboardingSlideRead.model_validate(slide) for slide in slides],
        state=OnboardingStateRead(
            last_completed_order=state.last_completed_order,
            is_completed=state.is_completed,
        ),
        next_order=next_order,
    )


@router.post("/complete", response_model=OnboardingStateRead, summary="Завершаем шаг онбординга")
def complete_onboarding_step(
    payload: OnboardingCompleteRequest,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OnboardingStateRead:
    """Фиксируем прохождение очередного шага лора."""

    try:
        state = complete_slide(db, current_user, payload.order)
    except ValueError as exc:  # pragma: no cover - ошибка бизнес-логики
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return OnboardingStateRead(
        last_completed_order=state.last_completed_order,
        is_completed=state.is_completed,
    )


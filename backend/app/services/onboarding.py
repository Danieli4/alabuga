"""Сервисный слой для онбординга."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.onboarding import OnboardingSlide, OnboardingState
from app.models.user import User


def _ensure_state(db: Session, user: User) -> OnboardingState:
    """Гарантируем наличие записи о прогрессе."""

    if user.onboarding_state:
        return user.onboarding_state

    state = OnboardingState(user_id=user.id, last_completed_order=0, is_completed=False)
    db.add(state)
    db.flush()
    db.refresh(state)
    return state


def get_overview(db: Session, user: User) -> tuple[list[OnboardingSlide], OnboardingState, int | None]:
    """Возвращаем все слайды и текущий прогресс."""

    slides = db.query(OnboardingSlide).order_by(OnboardingSlide.order).all()
    state = _ensure_state(db, user)

    next_slide = next((slide for slide in slides if slide.order > state.last_completed_order), None)
    next_order: int | None = next_slide.order if next_slide else None
    return slides, state, next_order


def complete_slide(db: Session, user: User, order: int) -> OnboardingState:
    """Фиксируем завершение шага, если это корректный порядок."""

    slides = db.query(OnboardingSlide).order_by(OnboardingSlide.order).all()
    if not slides:
        raise ValueError("Онбординг ещё не настроен")

    state = _ensure_state(db, user)

    allowed_orders = [slide.order for slide in slides]
    if order not in allowed_orders:
        raise ValueError("Неизвестный шаг онбординга")

    if order <= state.last_completed_order:
        return state

    expected_order = next((value for value in allowed_orders if value > state.last_completed_order), None)
    if expected_order is None or order != expected_order:
        raise ValueError("Сначала завершите предыдущие шаги")

    state.last_completed_order = order
    state.is_completed = order == allowed_orders[-1]
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


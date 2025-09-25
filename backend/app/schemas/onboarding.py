"""Схемы для онбординга."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class OnboardingSlideRead(BaseModel):
    """Отдельный слайд онбординга."""

    id: int
    order: int
    title: str
    body: str
    media_url: Optional[str]
    cta_text: Optional[str]
    cta_link: Optional[str]

    class Config:
        from_attributes = True


class OnboardingStateRead(BaseModel):
    """Прогресс пользователя."""

    last_completed_order: int
    is_completed: bool


class OnboardingOverview(BaseModel):
    """Полный ответ с прогрессом и контентом."""

    slides: list[OnboardingSlideRead]
    state: OnboardingStateRead
    next_order: int | None


class OnboardingCompleteRequest(BaseModel):
    """Запрос на фиксацию завершения шага."""

    order: int


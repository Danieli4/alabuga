"""Модели онбординга и лора."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Integer, String, Text, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class OnboardingSlide(Base, TimestampMixin):
    """Контентный слайд онбординга, который видит пилот."""

    __tablename__ = "onboarding_slides"
    __table_args__ = (UniqueConstraint("order", name="uq_onboarding_slide_order"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(160), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    media_url: Mapped[Optional[str]] = mapped_column(String(512))
    cta_text: Mapped[Optional[str]] = mapped_column(String(120))
    cta_link: Mapped[Optional[str]] = mapped_column(String(512))


class OnboardingState(Base, TimestampMixin):
    """Прогресс пользователя по онбордингу."""

    __tablename__ = "onboarding_states"
    __table_args__ = (UniqueConstraint("user_id", name="uq_onboarding_state_user"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    last_completed_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user = relationship("User", back_populates="onboarding_state")


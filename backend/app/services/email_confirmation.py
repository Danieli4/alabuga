"""Вспомогательные функции для подтверждения электронной почты."""

from __future__ import annotations

from datetime import datetime, timezone
from secrets import token_urlsafe

from sqlalchemy.orm import Session

from app.models.user import User


def issue_confirmation_token(user: User, db: Session) -> str:
    """Генерируем и сохраняем одноразовый код подтверждения."""

    token = token_urlsafe(16)
    user.email_confirmation_token = token
    user.is_email_confirmed = False
    user.email_confirmed_at = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return token


def confirm_email(user: User, db: Session) -> None:
    """Помечаем почту подтверждённой."""

    user.is_email_confirmed = True
    user.email_confirmation_token = None
    user.email_confirmed_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)

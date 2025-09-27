"""Вспомогательные функции для подтверждения электронной почты."""

from __future__ import annotations

from datetime import datetime, timezone
from secrets import token_urlsafe

from sqlalchemy.orm import Session

from app.models.user import User


def issue_confirmation_token(user: User, db: Session) -> str:
    """Генерируем и сохраняем одноразовый код подтверждения."""

    # В `token_urlsafe(16)` мы просим secrets создать криптостойкую строку длиной ~22 символа,
    # которую удобно вводить вручную. Каждый новый вызов полностью обнуляет предыдущий код.
    token = token_urlsafe(16)
    # Сбрасываем флаги подтверждения — это важно, если пользователь запрашивает
    # повторное письмо: только введя актуальный код, он снова активируется.
    user.email_confirmation_token = token
    user.is_email_confirmed = False
    user.email_confirmed_at = None
    db.add(user)
    db.commit()
    db.refresh(user)
    return token


def confirm_email(user: User, db: Session) -> None:
    """Помечаем почту подтверждённой."""

    # Флаг `is_email_confirmed` избавляет нас от лишних запросов при каждой авторизации.
    user.is_email_confirmed = True
    # Токен больше не нужен — удаляем его, чтобы предотвратить повторное использование.
    user.email_confirmation_token = None
    # Сохраняем точное время подтверждения: пригодится в аналитике и для аудита.
    user.email_confirmed_at = datetime.now(timezone.utc)
    db.add(user)
    db.commit()
    db.refresh(user)

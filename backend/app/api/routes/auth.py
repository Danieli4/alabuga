"""Маршруты аутентификации."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import EmailConfirm, EmailRequest, Token
from app.schemas.user import UserLogin, UserRead
from app.services.email_confirmation import confirm_email as mark_confirmed
from app.services.email_confirmation import issue_confirmation_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token, summary="Авторизация по email и паролю")
def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Проверяем логин и выдаём JWT."""

    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные данные")

    if settings.require_email_confirmation and not user.is_email_confirmed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подтвердите e-mail, прежде чем войти",
        )

    token = create_access_token(user.email, timedelta(minutes=settings.access_token_expire_minutes))
    return Token(access_token=token)


@router.get("/me", response_model=UserRead, summary="Текущий пользователь")
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    """Простая проверка токена."""

    return current_user


@router.post("/request-confirmation", summary="Повторная отправка письма с кодом")
def request_confirmation(payload: EmailRequest, db: Session = Depends(get_db)) -> dict[str, str | None]:
    """Генерируем код подтверждения и в режиме разработки возвращаем его в ответе."""

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    token = issue_confirmation_token(user, db)

    hint = None
    if settings.environment != 'production':
        hint = token

    return {
        "detail": "Письмо с подтверждением отправлено. Проверьте почту.",
        "debug_token": hint,
    }


@router.post("/confirm", summary="Подтверждаем e-mail по коду")
def confirm_email(payload: EmailConfirm, db: Session = Depends(get_db)) -> dict[str, str]:
    """Активируем почту, если код совпал."""

    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if not user.email_confirmation_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Код не запрошен")

    if user.email_confirmation_token != payload.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный код")

    mark_confirmed(user, db)
    return {"detail": "E-mail подтверждён"}

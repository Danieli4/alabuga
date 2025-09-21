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
from app.schemas.auth import Token
from app.schemas.user import UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token, summary="Авторизация по email и паролю")
def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Проверяем логин и выдаём JWT."""

    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные данные")

    token = create_access_token(user.email, timedelta(minutes=settings.access_token_expire_minutes))
    return Token(access_token=token)


@router.get("/me", response_model=UserRead, summary="Текущий пользователь")
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    """Простая проверка токена."""

    return current_user

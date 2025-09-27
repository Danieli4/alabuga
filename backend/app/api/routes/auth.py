"""Маршруты аутентификации."""

from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.session import get_db
from app.models.rank import Rank
from app.models.user import User, UserRole
from app.schemas.auth import EmailConfirm, EmailRequest, Token
from app.schemas.user import UserLogin, UserRead, UserRegister
from app.services.email_confirmation import confirm_email as mark_confirmed
from app.services.email_confirmation import issue_confirmation_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token, summary="Авторизация по email и паролю")
def login(user_in: UserLogin, db: Session = Depends(get_db)) -> Token:
    """Проверяем логин и выдаём JWT."""

    # 1. Находим пользователя по e-mail. Для супер-новичка: `.first()` вернёт
    #    сам объект пользователя либо `None`, если почта не зарегистрирована.
    user = db.query(User).filter(User.email == user_in.email).first()
    # 2. Если пользователь не найден или пароль не совпал — сразу возвращаем 401.
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные данные")

    if settings.require_email_confirmation and not user.is_email_confirmed:
        # 3. Когда включено подтверждение почты, запрещаем вход до завершения процедуры.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Подтвердите e-mail, прежде чем войти",
        )

    # 4. Генерируем короткоживущий JWT. Он будет храниться в httpOnly-cookie на фронте.
    token = create_access_token(user.email, timedelta(minutes=settings.access_token_expire_minutes))
    return Token(access_token=token)


@router.post(
    "/register",
    response_model=Token | dict[str, str | None],
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пилота",
)
def register(user_in: UserRegister, db: Session = Depends(get_db)) -> Token | dict[str, str | None]:
    """Создаём учётную запись пилота и при необходимости отправляем код подтверждения."""

    # 1. Проверяем, не зарегистрирован ли пользователь раньше: уникальный e-mail — обязательное условие.
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким email уже существует")

    # 2. Назначаем новичку самый базовый ранг. Если ранги ещё не заведены в БД,
    #    `base_rank` будет `None`, поэтому ниже используем условный оператор.
    base_rank = db.query(Rank).order_by(Rank.required_xp).first()
    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=get_password_hash(user_in.password),
        role=UserRole.PILOT,
        preferred_branch=user_in.preferred_branch,
        motivation=user_in.motivation,
        current_rank_id=base_rank.id if base_rank else None,
        is_email_confirmed=not settings.require_email_confirmation,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if settings.require_email_confirmation:
        # 3. При включённом подтверждении выдаём одноразовый код и подсказываем,
        #    что делать дальше. В dev-режиме отдаём код прямо в ответе, чтобы QA
        #    мог пройти сценарий без почтового сервиса.
        token = issue_confirmation_token(user, db)
        return {
            "detail": "Мы отправили письмо с подтверждением. Введите код, чтобы активировать аккаунт.",
            "debug_token": token if settings.environment != 'production' else None,
        }

    # 4. Если подтверждение выключено, сразу создаём JWT и возвращаем его фронтенду.
    access_token = create_access_token(user.email, timedelta(minutes=settings.access_token_expire_minutes))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead, summary="Текущий пользователь")
def read_current_user(current_user: User = Depends(get_current_user)) -> UserRead:
    """Простая проверка токена."""

    return current_user


@router.post("/request-confirmation", summary="Повторная отправка письма с кодом")
def request_confirmation(payload: EmailRequest, db: Session = Depends(get_db)) -> dict[str, str | None]:
    """Генерируем код подтверждения и в режиме разработки возвращаем его в ответе."""

    # 1. Находим пользователя и убеждаемся, что он вообще существует.
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    # 2. Генерируем новый код подтверждения, предыдущий становится недействительным.
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

    # 1. Повторяем поиск пользователя: это второй шаг флоу подтверждения.
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")

    if not user.email_confirmation_token:
        # 2. Если токена нет, значит пользователь не запрашивал письмо.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Код не запрошен")

    if user.email_confirmation_token != payload.token:
        # 3. Защищаемся от неправильного кода.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Неверный код")

    # 4. Отмечаем почту подтверждённой и убираем токен.
    mark_confirmed(user, db)
    return {"detail": "E-mail подтверждён"}

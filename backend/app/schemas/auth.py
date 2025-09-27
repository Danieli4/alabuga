"""Схемы авторизации."""

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Ответ с токеном."""

    access_token: str
    token_type: str = "bearer"


class EmailRequest(BaseModel):
    """Запрос на повторную отправку письма."""

    email: EmailStr


class EmailConfirm(BaseModel):
    """Подтверждение e-mail по коду."""

    email: EmailStr
    token: str

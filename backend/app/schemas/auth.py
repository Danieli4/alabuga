"""Схемы авторизации."""

from pydantic import BaseModel


class Token(BaseModel):
    """Ответ с токеном."""

    access_token: str
    token_type: str = "bearer"

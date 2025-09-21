"""Pydantic-схемы для пользователей и компетенций."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import CompetencyCategory, UserRole


class CompetencyBase(BaseModel):
    """Базовое описание компетенции."""

    id: int
    name: str
    description: str
    category: CompetencyCategory

    class Config:
        from_attributes = True


class UserCompetencyRead(BaseModel):
    """Информация о компетенции пользователя."""

    competency: CompetencyBase
    level: int

    class Config:
        from_attributes = True


class UserArtifactRead(BaseModel):
    """Полученный артефакт."""

    id: int
    name: str
    description: str
    rarity: str
    image_url: Optional[str]

    class Config:
        from_attributes = True


class UserRead(BaseModel):
    """Схема чтения пользователя."""

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    xp: int
    mana: int
    current_rank_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(UserRead):
    """Профиль с расширенной информацией."""

    competencies: list[UserCompetencyRead]
    artifacts: list[UserArtifactRead]


class UserCreate(BaseModel):
    """Создание пользователя (используется для сидов)."""

    email: EmailStr
    full_name: str
    password: str
    role: UserRole = UserRole.PILOT


class UserLogin(BaseModel):
    """Данные для входа."""

    email: EmailStr
    password: str

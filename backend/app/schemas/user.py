"""Pydantic-схемы для пользователей и компетенций."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.models.user import CompetencyCategory, UserRole
from app.schemas.artifact import ArtifactRead


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
    """Полученный пользователем артефакт с датой выдачи."""

    id: int
    artifact: ArtifactRead
    created_at: datetime

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
    is_email_confirmed: bool
    email_confirmed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserProfile(UserRead):
    """Профиль с расширенной информацией."""

    competencies: list[UserCompetencyRead]
    artifacts: list[UserArtifactRead]


class LeaderboardEntry(BaseModel):
    """Строка лидерборда по опыту и компетенциям."""

    user_id: int
    full_name: str
    rank_title: Optional[str]
    xp: int
    mana: int
    completed_missions: int
    competencies: list[UserCompetencyRead]

    class Config:
        from_attributes = True


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


class UserRegister(BaseModel):
    """Регистрация нового пилота."""

    email: EmailStr
    full_name: str
    password: str
    # Дополнительные сведения помогают персонализировать онбординг и связать пилота с куратором.
    preferred_branch: Optional[str] = None
    motivation: Optional[str] = None

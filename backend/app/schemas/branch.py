"""Схемы веток миссий."""

from __future__ import annotations

from pydantic import BaseModel


class BranchMissionRead(BaseModel):
    """Миссия внутри ветки."""

    mission_id: int
    mission_title: str
    order: int
    is_completed: bool = False
    is_available: bool = False


class BranchRead(BaseModel):
    """Описание ветки."""

    id: int
    title: str
    description: str
    category: str
    missions: list[BranchMissionRead]
    total_missions: int = 0
    completed_missions: int = 0

    class Config:
        from_attributes = True


class BranchCreate(BaseModel):
    """Создание ветки."""

    title: str
    description: str
    category: str


class BranchUpdate(BranchCreate):
    """Обновление ветки."""

    pass

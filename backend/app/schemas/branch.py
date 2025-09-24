"""Схемы веток миссий."""

from __future__ import annotations

from pydantic import BaseModel


class BranchMissionRead(BaseModel):
    """Миссия внутри ветки."""

    mission_id: int
    mission_title: str
    order: int


class BranchRead(BaseModel):
    """Описание ветки."""

    id: int
    title: str
    description: str
    category: str
    missions: list[BranchMissionRead]

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

"""Схемы рангов."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class RankBase(BaseModel):
    """Базовая информация о ранге."""

    id: int
    title: str
    description: str
    required_xp: int

    class Config:
        from_attributes = True


class RankRequirementMission(BaseModel):
    """Обязательная миссия."""

    mission_id: int
    mission_title: str


class RankRequirementCompetency(BaseModel):
    """Требование к компетенции."""

    competency_id: int
    competency_name: str
    required_level: int


class RankDetailed(RankBase):
    """Полный ранг со списком условий."""

    mission_requirements: list[RankRequirementMission]
    competency_requirements: list[RankRequirementCompetency]
    created_at: datetime
    updated_at: datetime

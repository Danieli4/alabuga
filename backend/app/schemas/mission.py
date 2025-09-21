"""Схемы миссий."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.mission import MissionDifficulty, SubmissionStatus


class MissionBase(BaseModel):
    """Минимальная информация о миссии."""

    id: int
    title: str
    description: str
    xp_reward: int
    mana_reward: int
    difficulty: MissionDifficulty
    is_active: bool

    class Config:
        from_attributes = True


class MissionCompetencyRewardRead(BaseModel):
    """Прокачка компетенции за миссию."""

    competency_id: int
    competency_name: str
    level_delta: int


class MissionDetail(MissionBase):
    """Полная карточка миссии."""

    minimum_rank_id: Optional[int]
    artifact_id: Optional[int]
    prerequisites: list[int]
    competency_rewards: list[MissionCompetencyRewardRead]
    created_at: datetime
    updated_at: datetime



class MissionCreateReward(BaseModel):
    """Описание награды компетенции при создании миссии."""

    competency_id: int
    level_delta: int = 1


class MissionCreate(BaseModel):
    """Схема создания миссии."""

    title: str
    description: str
    xp_reward: int
    mana_reward: int
    difficulty: MissionDifficulty = MissionDifficulty.MEDIUM
    minimum_rank_id: Optional[int] = None
    artifact_id: Optional[int] = None
    prerequisite_ids: list[int] = []
    competency_rewards: list[MissionCreateReward] = []
    branch_id: Optional[int] = None
    branch_order: int = 1


class MissionSubmissionCreate(BaseModel):
    """Отправка отчёта по миссии."""

    comment: Optional[str] = None
    proof_url: Optional[str] = None


class MissionSubmissionRead(BaseModel):
    """Получение статуса отправки."""

    mission_id: int
    status: SubmissionStatus
    comment: Optional[str]
    proof_url: Optional[str]
    awarded_xp: int
    awarded_mana: int
    updated_at: datetime

    class Config:
        from_attributes = True

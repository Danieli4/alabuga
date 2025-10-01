"""Схемы миссий."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, computed_field

from app.models.mission import MissionDifficulty, MissionFormat, SubmissionStatus


class MissionBase(BaseModel):
    """Минимальная информация о миссии."""

    id: int
    title: str
    description: str
    xp_reward: int
    mana_reward: int
    difficulty: MissionDifficulty
    format: MissionFormat
    event_location: Optional[str] = None
    event_address: Optional[str] = None
    event_starts_at: Optional[datetime] = None
    event_ends_at: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    registration_url: Optional[str] = None
    registration_notes: Optional[str] = None
    capacity: Optional[int] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: bool
    is_available: bool = True
    locked_reasons: list[str] = Field(default_factory=list)
    is_completed: bool = False
    requires_documents: bool = False
    has_coding_challenges: bool = False
    coding_challenge_count: int = 0
    completed_coding_challenges: int = 0
    submission_status: Optional[SubmissionStatus] = None
    registered_participants: int = 0
    registration_open: bool = True

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
    format: MissionFormat = MissionFormat.ONLINE
    event_location: Optional[str] = None
    event_address: Optional[str] = None
    event_starts_at: Optional[datetime] = None
    event_ends_at: Optional[datetime] = None
    registration_deadline: Optional[datetime] = None
    registration_url: Optional[str] = None
    registration_notes: Optional[str] = None
    capacity: Optional[int] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    minimum_rank_id: Optional[int] = None
    artifact_id: Optional[int] = None
    prerequisite_ids: list[int] = []
    competency_rewards: list[MissionCreateReward] = []
    branch_id: Optional[int] = None
    branch_order: int = 1


class MissionUpdate(BaseModel):
    """Схема обновления миссии."""

    title: Optional[str] = None
    description: Optional[str] = None
    xp_reward: Optional[int] = None
    mana_reward: Optional[int] = None
    difficulty: Optional[MissionDifficulty] = None
    format: Optional[MissionFormat] = None
    event_location: Optional[str | None] = None
    event_address: Optional[str | None] = None
    event_starts_at: Optional[datetime | None] = None
    event_ends_at: Optional[datetime | None] = None
    registration_deadline: Optional[datetime | None] = None
    registration_url: Optional[str | None] = None
    registration_notes: Optional[str | None] = None
    capacity: Optional[int | None] = None
    contact_person: Optional[str | None] = None
    contact_phone: Optional[str | None] = None
    minimum_rank_id: Optional[int | None] = None
    artifact_id: Optional[int | None] = None
    prerequisite_ids: Optional[list[int]] = None
    competency_rewards: Optional[list[MissionCreateReward]] = None
    branch_id: Optional[int | None] = None
    branch_order: Optional[int] = None
    is_active: Optional[bool] = None


class MissionSubmissionCreate(BaseModel):
    """Отправка отчёта по миссии."""

    comment: Optional[str] = None
    proof_url: Optional[str] = None
    resume_link: Optional[str] = None


class MissionSubmissionRead(BaseModel):
    """Получение статуса отправки."""

    id: int
    mission_id: int
    status: SubmissionStatus
    comment: Optional[str]
    proof_url: Optional[str]
    resume_link: Optional[str]
    awarded_xp: int
    awarded_mana: int
    updated_at: datetime
    passport_path: Optional[str] = Field(default=None, exclude=True)
    photo_path: Optional[str] = Field(default=None, exclude=True)
    resume_path: Optional[str] = Field(default=None, exclude=True)

    class Config:
        from_attributes = True

    @computed_field  # type: ignore[misc]
    @property
    def passport_url(self) -> Optional[str]:
        """Ссылка для скачивания файла паспорта."""

        if self.passport_path:
            return f"/api/missions/submissions/{self.id}/files/passport"
        return None

    @computed_field  # type: ignore[misc]
    @property
    def photo_url(self) -> Optional[str]:
        """Ссылка на загруженную фотографию."""

        if self.photo_path:
            return f"/api/missions/submissions/{self.id}/files/photo"
        return None

    @computed_field  # type: ignore[misc]
    @property
    def resume_url(self) -> Optional[str]:
        """Ссылка на загруженный файл резюме."""

        if self.resume_path:
            return f"/api/missions/submissions/{self.id}/files/resume"
        return None

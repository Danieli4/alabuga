"""Схемы артефактов."""

from __future__ import annotations

from pydantic import BaseModel

from app.models.artifact import ArtifactRarity


class ArtifactRead(BaseModel):
    """Краткая информация об артефакте."""

    id: int
    name: str
    description: str
    rarity: ArtifactRarity
    image_url: str | None = None
    is_profile_modifier: bool = False
    background_effect: str | None = None
    profile_effect: str | None = None
    modifier_description: str | None = None

    class Config:
        from_attributes = True


class ArtifactCreate(BaseModel):
    """Создание артефакта."""

    name: str
    description: str
    rarity: ArtifactRarity
    image_url: str | None = None
    is_profile_modifier: bool = False
    background_effect: str | None = None
    profile_effect: str | None = None
    modifier_description: str | None = None


class ArtifactUpdate(BaseModel):
    """Обновление артефакта."""

    name: str | None = None
    description: str | None = None
    rarity: ArtifactRarity | None = None
    image_url: str | None = None
    is_profile_modifier: bool | None = None
    background_effect: str | None = None
    profile_effect: str | None = None
    modifier_description: str | None = None

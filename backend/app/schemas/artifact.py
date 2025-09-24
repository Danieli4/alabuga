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

    class Config:
        from_attributes = True

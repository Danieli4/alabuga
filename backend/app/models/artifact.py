"""Артефакты и магазинные предметы."""

from __future__ import annotations

from enum import Enum
from typing import List

from sqlalchemy import Boolean, Enum as SQLEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ArtifactRarity(str, Enum):
    """Редкость артефакта."""

    COMMON = "common"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


class Artifact(Base, TimestampMixin):
    """Артефакт, который можно получить за миссию."""

    __tablename__ = "artifacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    rarity: Mapped[ArtifactRarity] = mapped_column(SQLEnum(ArtifactRarity), nullable=False)
    image_url: Mapped[str] = mapped_column(String(512), nullable=True)
    
    # Модификаторы профиля (косметические эффекты)
    is_profile_modifier: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    background_effect: Mapped[str] = mapped_column(String(255), nullable=True)  # CSS для фона профиля
    profile_effect: Mapped[str] = mapped_column(String(255), nullable=True)  # Дополнительный эффект
    modifier_description: Mapped[str] = mapped_column(Text, nullable=True)

    missions: Mapped[List["Mission"]] = relationship("Mission", back_populates="artifact")
    pilots: Mapped[List["UserArtifact"]] = relationship("UserArtifact", back_populates="artifact")

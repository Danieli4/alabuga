"""Pydantic-схемы для отображения прогресса по рангу."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ProgressRank(BaseModel):
    """Краткое описание ранга, пригодное для отображения на дашборде."""

    id: int
    title: str
    description: str
    required_xp: int

    class Config:
        from_attributes = True


class ProgressXPMetrics(BaseModel):
    """Статистика по опыту: от базового значения до целевого порога."""

    baseline: int = Field(description="Количество XP, с которого начинается текущий этап прогресса")
    current: int = Field(description="Текущее значение XP пользователя")
    target: int = Field(description="Порог XP, необходимый для следующего ранга")
    remaining: int = Field(description="Сколько XP осталось набрать")
    progress_percent: float = Field(description="Прогресс на отрезке от baseline до target в долях единицы")


class ProgressMissionRequirement(BaseModel):
    """Статус обязательной миссии для следующего ранга."""

    mission_id: int
    mission_title: str
    is_completed: bool


class ProgressCompetencyRequirement(BaseModel):
    """Статус требования по компетенции."""

    competency_id: int
    competency_name: str
    required_level: int
    current_level: int
    is_met: bool


class ProgressSnapshot(BaseModel):
    """Итоговая структура прогресса: XP, обязательные миссии и компетенции."""

    current_rank: ProgressRank | None
    next_rank: ProgressRank | None
    xp: ProgressXPMetrics
    mission_requirements: list[ProgressMissionRequirement]
    competency_requirements: list[ProgressCompetencyRequirement]
    completed_missions: int
    total_missions: int
    met_competencies: int
    total_competencies: int

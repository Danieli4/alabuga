"""Схемы для миссий с задачами на программирование."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CodingChallengeState(BaseModel):
    """Описание шага миссии для фронтенда."""

    id: int
    order: int
    title: str
    prompt: str
    starter_code: Optional[str] = None
    is_passed: bool = False
    is_unlocked: bool = False
    last_submitted_code: Optional[str] = None
    last_stdout: Optional[str] = None
    last_stderr: Optional[str] = None
    last_exit_code: Optional[int] = None
    updated_at: Optional[datetime] = None


class CodingMissionState(BaseModel):
    """Состояние всей миссии: прогресс и список задач."""

    mission_id: int
    total_challenges: int
    completed_challenges: int
    current_challenge_id: Optional[int]
    is_mission_completed: bool
    challenges: list[CodingChallengeState]


class CodingRunRequest(BaseModel):
    """Запрос на запуск решения."""

    code: str = Field(..., min_length=1, description="Исходный код на Python")


class CodingRunResponse(BaseModel):
    """Ответ после запуска кода пользователя."""

    attempt_id: int
    stdout: str
    stderr: str
    exit_code: int
    is_passed: bool
    mission_completed: bool
    expected_output: Optional[str] = None


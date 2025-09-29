"""Pydantic-схемы для Python-миссии."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PythonSubmissionRead(BaseModel):
    """История попыток по конкретному заданию."""

    id: int
    challenge_id: int
    code: str
    stdout: Optional[str]
    stderr: Optional[str]
    is_passed: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PythonChallengeRead(BaseModel):
    """Описание задания, доступное пользователю."""

    id: int
    order: int
    title: str
    description: str
    input_data: Optional[str]
    starter_code: Optional[str]

    class Config:
        from_attributes = True


class PythonMissionState(BaseModel):
    """Сводка по прогрессу в Python-миссии."""

    mission_id: int
    total_challenges: int
    completed_challenges: int
    is_completed: bool
    next_challenge: Optional[PythonChallengeRead]
    last_submissions: list[PythonSubmissionRead]
    last_code: Optional[str] = None


class PythonSubmitRequest(BaseModel):
    """Запрос на проверку решения задачи."""

    challenge_id: int
    code: str

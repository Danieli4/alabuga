"""Сводные метрики для HR."""

from __future__ import annotations

from pydantic import BaseModel


class SubmissionStats(BaseModel):
    """Структура статистики по отправкам миссий."""

    pending: int
    approved: int
    rejected: int


class BranchCompletionStat(BaseModel):
    """Завершённость ветки."""

    branch_id: int
    branch_title: str
    completion_rate: float


class AdminDashboardStats(BaseModel):
    """Ответ с основными метриками."""

    total_users: int
    active_pilots: int
    average_completed_missions: float
    submission_stats: SubmissionStats
    branch_completion: list[BranchCompletionStat]

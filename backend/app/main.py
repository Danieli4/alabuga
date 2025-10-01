"""Точка входа FastAPI."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app import models  # noqa: F401 - важно, чтобы Base знала обо всех моделях
from app.api.routes import admin, auth, journal, missions, onboarding, store, users, python
from app.core.config import settings
from app.db.seed import seed


app = FastAPI(title=settings.project_name)


def create_demo_data() -> None:
    """Создаём демо-данные для разработки и тестирования.
    
    Использует модульную систему seed из app.db.seed для создания
    полного набора демо-данных включая пользователей, миссии, артефакты и т.д.
    """
    seed()


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(missions.router)
app.include_router(journal.router)
app.include_router(onboarding.router)
app.include_router(store.router)
app.include_router(python.router)
app.include_router(admin.router)


@app.on_event("startup")
async def on_startup() -> None:
    """При запуске обновляем схему БД и подготавливаем демо-данные."""

    if settings.environment != "production":
        create_demo_data()


@app.get("/", summary="Проверка работоспособности")
def healthcheck() -> dict[str, str]:
    """Простой ответ для Docker healthcheck."""

    return {"status": "ok", "environment": settings.environment}

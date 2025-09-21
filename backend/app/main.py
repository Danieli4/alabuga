"""Точка входа FastAPI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin, auth, journal, missions, store, users
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base

app = FastAPI(title=settings.project_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    """Создаём таблицы, если миграции ещё не применены."""

    Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(missions.router)
app.include_router(journal.router)
app.include_router(store.router)
app.include_router(admin.router)


@app.get("/", summary="Проверка работоспособности")
def healthcheck() -> dict[str, str]:
    """Простой ответ для Docker healthcheck."""

    return {"status": "ok", "environment": settings.environment}

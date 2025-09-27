"""Точка входа FastAPI."""

from __future__ import annotations

from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.api.routes import admin, auth, journal, missions, onboarding, store, users
from app.core.config import settings
from app.db.session import engine

ALEMBIC_CONFIG = Path(__file__).resolve().parents[1] / "alembic.ini"

app = FastAPI(title=settings.project_name)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def run_migrations() -> None:
    """Гарантируем, что база обновлена до последней схемы Alembic."""

    config = Config(str(ALEMBIC_CONFIG))
    config.set_main_option("sqlalchemy.url", str(settings.database_url))
    inspector = inspect(engine)
    script = ScriptDirectory.from_config(config)
    head_revision = script.get_current_head()

    tables = inspector.get_table_names()
    current_revision: str | None = None

    if "alembic_version" in tables:
        with engine.begin() as conn:
            row = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).fetchone()
            current_revision = row[0] if row else None

    if "alembic_version" not in tables or current_revision is None:
        if tables:
            # База создана через Base.metadata.create_all. Добавляем отсутствующие поля вручную
            # и фиксируем версию как актуальную, чтобы последующие миграции применялись штатно.
            user_columns = {col["name"] for col in inspector.get_columns("users")}
            with engine.begin() as conn:
                if "preferred_branch" not in user_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN preferred_branch VARCHAR(160)"))
                if "motivation" not in user_columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN motivation TEXT"))
                conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
                conn.execute(text("DELETE FROM alembic_version"))
                conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:rev)"), {"rev": head_revision})
            return
        # Таблиц ещё нет — создадим их миграциями.
        command.upgrade(config, "head")
        return

    command.upgrade(config, "head")


@app.on_event("startup")
def on_startup() -> None:
    """Прогоняем миграции перед обработкой запросов."""

    run_migrations()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(missions.router)
app.include_router(journal.router)
app.include_router(onboarding.router)
app.include_router(store.router)
app.include_router(admin.router)


@app.get("/", summary="Проверка работоспособности")
def healthcheck() -> dict[str, str]:
    """Простой ответ для Docker healthcheck."""

    return {"status": "ok", "environment": settings.environment}

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
from app.core.security import get_password_hash
from app.db.session import SessionLocal, engine
from app.models.rank import Rank
from app.models.user import User, UserRole

ALEMBIC_CONFIG = Path(__file__).resolve().parents[1] / "alembic.ini"

app = FastAPI(title=settings.project_name)


def run_migrations() -> None:
    """Прогоняем миграции Alembic, поддерживая легаси-базы без alembic_version."""

    config = Config(str(ALEMBIC_CONFIG))
    config.set_main_option("sqlalchemy.url", str(settings.database_url))
    # Alembic трактует относительный script_location относительно текущей рабочей
    # директории процесса. В тестах и фронтенд-сервере мы запускаем backend из
    # корня репозитория, поэтому явно подсказываем абсолютный путь до папки с
    # миграциями, чтобы `alembic` не падал с "Path doesn't exist: alembic".
    config.set_main_option(
        "script_location", str(Path(__file__).resolve().parents[1] / "alembic")
    )
    script = ScriptDirectory.from_config(config)
    head_revision = script.get_current_head()

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())

    current_revision: str | None = None
    if "alembic_version" in tables:
        with engine.begin() as conn:
            row = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).fetchone()
            current_revision = row[0] if row else None

    if "alembic_version" not in tables or current_revision is None:
        if not tables:
            command.upgrade(config, "head")
            return

        user_columns = set()
        if "users" in tables:
            user_columns = {column["name"] for column in inspector.get_columns("users")}

        submission_columns = set()
        if "mission_submissions" in tables:
            submission_columns = {column["name"] for column in inspector.get_columns("mission_submissions")}

        mission_columns = set()
        if "missions" in tables:
            mission_columns = {column["name"] for column in inspector.get_columns("missions")}

        with engine.begin() as conn:
            if "preferred_branch" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN preferred_branch VARCHAR(160)"))
            if "motivation" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN motivation TEXT"))

            if "passport_path" not in submission_columns:
                conn.execute(text("ALTER TABLE mission_submissions ADD COLUMN passport_path VARCHAR(512)"))
            if "photo_path" not in submission_columns:
                conn.execute(text("ALTER TABLE mission_submissions ADD COLUMN photo_path VARCHAR(512)"))
            if "resume_path" not in submission_columns:
                conn.execute(text("ALTER TABLE mission_submissions ADD COLUMN resume_path VARCHAR(512)"))
            if "resume_link" not in submission_columns:
                conn.execute(text("ALTER TABLE mission_submissions ADD COLUMN resume_link VARCHAR(512)"))

            if "missions" in tables:
                # Легаси-базы без alembic_version пропускали миграцию с офлайн-полями,
                # поэтому докидываем недостающие колонки вручную, чтобы API /admin не падало.
                if "format" not in mission_columns:
                    conn.execute(
                        text(
                            "ALTER TABLE missions ADD COLUMN format VARCHAR(20) NOT NULL DEFAULT 'online'"
                        )
                    )
                    conn.execute(text("UPDATE missions SET format = 'online' WHERE format IS NULL"))
                if "event_location" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN event_location VARCHAR(160)"))
                if "event_address" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN event_address VARCHAR(255)"))
                if "event_starts_at" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN event_starts_at TIMESTAMP"))
                if "event_ends_at" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN event_ends_at TIMESTAMP"))
                if "registration_deadline" not in mission_columns:
                    conn.execute(
                        text("ALTER TABLE missions ADD COLUMN registration_deadline TIMESTAMP")
                    )
                if "registration_url" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN registration_url VARCHAR(512)"))
                if "registration_notes" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN registration_notes TEXT"))
                if "capacity" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN capacity INTEGER"))
                if "contact_person" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN contact_person VARCHAR(120)"))
                if "contact_phone" not in mission_columns:
                    conn.execute(text("ALTER TABLE missions ADD COLUMN contact_phone VARCHAR(64)"))

            conn.execute(text("CREATE TABLE IF NOT EXISTS alembic_version (version_num VARCHAR(32) NOT NULL)"))
            conn.execute(text("DELETE FROM alembic_version"))
            conn.execute(text("INSERT INTO alembic_version (version_num) VALUES (:rev)"), {"rev": head_revision})

    command.upgrade(config, "head")


def create_demo_users() -> None:
    """Создаём демо-пользователей, чтобы упростить проверку сценариев."""

    session: Session = SessionLocal()
    try:
        pilot_exists = session.query(User).filter(User.email == "candidate@alabuga.space").first()
        hr_exists = session.query(User).filter(User.email == "hr@alabuga.space").first()

        if pilot_exists and hr_exists:
            return

        base_rank = session.query(Rank).order_by(Rank.required_xp).first()

        if not pilot_exists:
            pilot = User(
                email="candidate@alabuga.space",
                full_name="Алексей Пилотов",
                role=UserRole.PILOT,
                hashed_password=get_password_hash("orbita123"),
                current_rank_id=base_rank.id if base_rank else None,
                is_email_confirmed=True,
                preferred_branch="Получение оффера",
                motivation="Хочу пройти все миссии и закрепиться в экипаже.",
            )
            session.add(pilot)

        if not hr_exists:
            hr_rank = session.query(Rank).order_by(Rank.required_xp.desc()).first()
            hr = User(
                email="hr@alabuga.space",
                full_name="Мария HR",
                role=UserRole.HR,
                hashed_password=get_password_hash("orbita123"),
                current_rank_id=hr_rank.id if hr_rank else None,
                is_email_confirmed=True,
                preferred_branch="Куратор миссий",
            )
            session.add(hr)

        session.commit()
    finally:
        session.close()


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

    run_migrations()
    if settings.environment != "production":
        create_demo_users()


@app.get("/", summary="Проверка работоспособности")
def healthcheck() -> dict[str, str]:
    """Простой ответ для Docker healthcheck."""

    return {"status": "ok", "environment": settings.environment}

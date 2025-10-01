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
from app.models.user import User, UserRole, UserArtifact
from app.models.artifact import Artifact, ArtifactRarity


app = FastAPI(title=settings.project_name)


def create_demo_data() -> None:
    """Создаём демо-пользователей и артефакты для проверки сценариев."""

    session: Session = SessionLocal()
    try:
        pilot_exists = session.query(User).filter(User.email == "candidate@alabuga.space").first()
        hr_exists = session.query(User).filter(User.email == "hr@alabuga.space").first()

        # Создаём пользователей если их нет
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
            session.flush()  # Получаем ID пилота
        else:
            pilot = pilot_exists

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

        # Создаём демо-артефакты если их нет
        demo_artifacts = [
            {
                "name": "Путеводитель по Галактике",
                "description": "Легендарный справочник, содержащий ответы на все вопросы вселенной",
                "rarity": ArtifactRarity.LEGENDARY,
                "image_url": "/artifacts/putevoditel-galaktiki.jpg",
                "is_profile_modifier": True,
                "background_effect": "linear-gradient(135deg, rgba(108,92,231,0.4), rgba(0,184,148,0.3))",
                "profile_effect": "glow-legendary",
                "modifier_description": "Добавляет легендарное свечение и космический градиент к профилю"
            },
            {
                "name": "Полотенце 42",
                "description": "Самый полезный предмет для путешественника по галактике",
                "rarity": ArtifactRarity.EPIC,
                "image_url": "/artifacts/polotentse-42.jpg",
                "is_profile_modifier": True,
                "background_effect": "linear-gradient(135deg, rgba(255,118,117,0.3), rgba(253,203,110,0.3))",
                "profile_effect": "warm-glow",
                "modifier_description": "Придаёт профилю тёплое свечение и уютную атмосферу"
            },
            {
                "name": "Кнопка Невероятности",
                "description": "Устройство, способное изменить реальность самым невероятным образом",
                "rarity": ArtifactRarity.RARE,
                "image_url": "/artifacts/knopka-neveroyatnosti.jpg",
                "is_profile_modifier": True,
                "background_effect": "linear-gradient(135deg, rgba(162,155,254,0.3), rgba(108,92,231,0.3))",
                "profile_effect": "pulse-effect",
                "modifier_description": "Добавляет пульсирующий эффект и фиолетовое свечение"
            },
            {
                "name": "Сфера Марвина",
                "description": "Депрессивный, но невероятно умный робот в форме сферы",
                "rarity": ArtifactRarity.COMMON,
                "image_url": "/artifacts/sfera-marvina.jpg",
                "is_profile_modifier": False,
                "background_effect": None,
                "profile_effect": None,
                "modifier_description": None
            },
            {
                "name": "Пангалактический Грызлодёр",
                "description": "Лучший напиток во вселенной, эффект как от удара золотым кирпичом",
                "rarity": ArtifactRarity.EPIC,
                "image_url": "/artifacts/pangalakticheskiy-gryzloder.jpg",
                "is_profile_modifier": True,
                "background_effect": "linear-gradient(135deg, rgba(255,234,167,0.3), rgba(255,118,117,0.3))",
                "profile_effect": "shimmer",
                "modifier_description": "Добавляет мерцающий золотистый эффект к профилю"
            }
        ]

        for artifact_data in demo_artifacts:
            existing = session.query(Artifact).filter(Artifact.name == artifact_data["name"]).first()
            if not existing:
                artifact = Artifact(**artifact_data)
                session.add(artifact)
                session.flush()
                
                # Даём артефакты Алексею Пилотову
                if artifact_data["is_profile_modifier"]:
                    user_artifact = UserArtifact(user_id=pilot.id, artifact_id=artifact.id)
                    session.add(user_artifact)

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

    if settings.environment != "production":
        create_demo_data()


@app.get("/", summary="Проверка работоспособности")
def healthcheck() -> dict[str, str]:
    """Простой ответ для Docker healthcheck."""

    return {"status": "ok", "environment": settings.environment}

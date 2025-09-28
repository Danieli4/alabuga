"""Точка входа FastAPI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.routes import admin, auth, journal, missions, onboarding, store, users
from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.user import User, UserRole
from app.models.rank import Rank
# Import all models to ensure they're registered with Base.metadata
from app import models  # This imports all models through the __init__.py

app = FastAPI(title=settings.project_name)


def create_demo_users() -> None:
    """Create demo users if they don't exist."""
    session: Session = SessionLocal()
    try:
        # Check if demo users already exist
        pilot_exists = session.query(User).filter(User.email == "candidate@alabuga.space").first()
        hr_exists = session.query(User).filter(User.email == "hr@alabuga.space").first()
        
        if pilot_exists and hr_exists:
            print("✅ Demo users already exist")
            return
        
        # Get base rank (or None if no ranks exist)
        base_rank = session.query(Rank).order_by(Rank.required_xp).first()
        
        # Create pilot demo user
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
            print("✅ Created demo pilot user: candidate@alabuga.space / orbita123")
        
        # Create HR demo user
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
            print("✅ Created demo HR user: hr@alabuga.space / orbita123")
        
        session.commit()
    except Exception as e:
        print(f"❌ Failed to create demo users: {e}")
        session.rollback()
    finally:
        session.close()


app = FastAPI(title=settings.project_name)


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
app.include_router(admin.router)


@app.on_event("startup")
async def startup_event():
    """Create demo users on startup if in debug mode."""
    if settings.debug:
        create_demo_users()


@app.get("/", summary="Проверка работоспособности")
def healthcheck() -> dict[str, str]:
    """Простой ответ для Docker healthcheck."""

    return {"status": "ok"}

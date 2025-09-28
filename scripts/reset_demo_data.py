"""Удаление тестовых данных и вложений."""

from __future__ import annotations

import shutil

from pathlib import Path
import sys
import os

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'backend'))
sys.path.append(str(ROOT))

from app.main import run_migrations
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.mission import MissionSubmission
from app.models.store import Order
from app.models.journal import JournalEntry
from app.models.user import User
from scripts import seed_data


def reset() -> None:
    """Очищаем пользовательскую активность и загруженные документы."""

    db_file = settings.sqlite_path
    if db_file.exists():
        db_file.unlink()

    original_cwd = Path.cwd()
    try:
        os.chdir(ROOT / 'backend')
        run_migrations()
    finally:
        os.chdir(original_cwd)

    session: Session = SessionLocal()
    try:
        session.query(MissionSubmission).delete()
        session.query(Order).delete()
        session.query(JournalEntry).delete()

        # Сбрасываем опыт и ману демо-пользователям, чтобы они начинали «с нуля».
        for user in session.query(User).all():
            user.xp = 0
            user.mana = 0

        session.commit()
    finally:
        session.close()

    uploads_dir: Path = settings.uploads_path
    if uploads_dir.exists():
        shutil.rmtree(uploads_dir)
    uploads_dir.mkdir(parents=True, exist_ok=True)

    sentinel = settings.sqlite_path.parent / ".seeded"
    if sentinel.exists():
        sentinel.unlink()

    seed_data.seed()

    print("Demo data reset and reseeded with fresh hitchhiker-ready fixtures.")


if __name__ == "__main__":
    reset()

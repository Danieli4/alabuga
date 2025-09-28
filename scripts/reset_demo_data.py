"""Удаление тестовых данных и вложений."""

from __future__ import annotations

import shutil

from pathlib import Path
import sys

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'backend'))

from app.main import run_migrations
from app.core.config import settings
from app.db.session import SessionLocal
from app.models.mission import MissionSubmission
from app.models.store import Order
from app.models.journal import JournalEntry
from app.models.user import User


def reset() -> None:
    """Очищаем пользовательскую активность и загруженные документы."""

    run_migrations()

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

    print("Demo data cleared. Mission submissions, journal entries, orders и загруженные файлы удалены.")


if __name__ == "__main__":
    reset()

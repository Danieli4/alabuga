"""Настройка подключения к базе данных."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# echo=True полезно при отладке, но оставляем False по умолчанию.
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Зависимость FastAPI для получения сессии БД."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

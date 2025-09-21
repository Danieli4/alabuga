"""Фикстуры для тестов."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
TEST_DB = Path("/tmp/alabuga_test.db")
os.environ["ALABUGA_SQLITE_PATH"] = str(TEST_DB)

from app.core.config import settings  # noqa: E402
from app.db import base as db_base  # noqa: E402
from app.db.session import SessionLocal, engine  # noqa: E402
from app.models.base import Base  # noqa: E402


@pytest.fixture(autouse=True)
def _prepare_database():
    """Очищаем БД перед тестом."""

    if TEST_DB.exists():
        TEST_DB.unlink()
    engine.dispose()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db_session():
    """Предоставляем сессию SQLAlchemy."""

    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

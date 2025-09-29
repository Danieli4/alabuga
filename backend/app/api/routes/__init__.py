"""Экспортируем роутеры для подключения в приложении."""

from . import admin, auth, journal, missions, onboarding, store, users, python  # noqa: F401

__all__ = [
    "admin",
    "auth",
    "journal",
    "missions",
    "onboarding",
    "store",
    "users",
    "python",
]

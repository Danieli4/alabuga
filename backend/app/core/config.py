"""Конфигурация приложения и загрузка окружения."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Глобальные настройки сервиса."""

    model_config = SettingsConfigDict(env_file=".env", env_prefix="ALABUGA_", extra="ignore")

    project_name: str = "Alabuga Gamification API"
    environment: str = "local"
    secret_key: str = "super-secret-key-change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 12

    backend_cors_origins: list[str] = ["http://localhost:3000", "http://frontend:3000"]

    sqlite_path: Path = Path("/data/app.db")

    @property
    def database_url(self) -> str:
        """Путь к базе данных SQLite."""

        return f"sqlite:///{self.sqlite_path}"


@lru_cache()
def get_settings() -> Settings:
    """Кэшируем создание настроек, чтобы не читать файл каждый раз."""

    settings = Settings()
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return settings


settings = get_settings()

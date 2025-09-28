"""Database initialization and migration utilities."""

from __future__ import annotations

import sys
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.core.config import settings
from app.db.session import engine

ALEMBIC_CONFIG = Path(__file__).resolve().parents[2] / "alembic.ini"


def get_alembic_config() -> Config:
    """Get configured Alembic Config object."""
    config = Config(str(ALEMBIC_CONFIG))
    config.set_main_option("sqlalchemy.url", str(settings.database_url))
    return config


def check_database_connection() -> bool:
    """Check if database connection is working."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def run_migrations() -> bool:
    """Run database migrations to head."""
    try:
        config = get_alembic_config()
        command.upgrade(config, "head")
        print("✅ Database migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def init_database() -> bool:
    """Initialize database: check connection and run migrations."""
    print("🔄 Initializing database...")
    
    if not check_database_connection():
        print("❌ Cannot connect to database")
        return False
    
    if not run_migrations():
        print("❌ Failed to run migrations")
        return False
    
    print("✅ Database initialization completed successfully")
    return True


def main() -> None:
    """CLI entry point for database initialization."""
    success = init_database()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

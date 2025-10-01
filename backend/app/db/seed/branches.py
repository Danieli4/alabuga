"""Seed branches data."""

from sqlalchemy.orm import Session

from app.models.branch import Branch


def seed_branches(session: Session) -> dict[str, Branch]:
    """Create and return branches."""
    branch = Branch(
        title="Получение оффера",
        description="Путь кандидата от знакомства до выхода на орбиту",
        category="quest",
    )
    python_branch = Branch(
        title="Основы Python",
        description="Мини-курс из 10 задач для проверки синтаксиса и базовой логики.",
        category="training",
    )
    offline_branch = Branch(
        title="Офлайн мероприятия",
        description="Живые встречи в кампусе и городе",
        category="event",
    )
    session.add_all([branch, python_branch, offline_branch])
    session.flush()
    
    return {
        "main": branch,
        "python": python_branch,
        "offline": offline_branch,
    }

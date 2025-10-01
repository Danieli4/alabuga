"""Seed competencies data."""

from sqlalchemy.orm import Session

from app.models.user import Competency, CompetencyCategory


def seed_competencies(session: Session) -> list[Competency]:
    """Create and return competencies."""
    competencies = [
        Competency(
            name="Навигация",
            description="Умение ориентироваться в процессах Алабуги",
            category=CompetencyCategory.ANALYTICS,
        ),
        Competency(
            name="Коммуникация",
            description="Чётко объяснять свои идеи",
            category=CompetencyCategory.COMMUNICATION,
        ),
        Competency(
            name="Инженерия",
            description="Работа с технологиями и оборудованием",
            category=CompetencyCategory.TECH,
        ),
        Competency(
            name="Командная работа",
            description="Поддержка экипажа",
            category=CompetencyCategory.TEAMWORK,
        ),
        Competency(
            name="Лидерство",
            description="Вести за собой",
            category=CompetencyCategory.LEADERSHIP,
        ),
        Competency(
            name="Культура",
            description="Следование лору Алабуги",
            category=CompetencyCategory.CULTURE,
        ),
    ]
    session.add_all(competencies)
    session.flush()
    return competencies

"""Наполнение демонстрационными данными."""

from __future__ import annotations

from pathlib import Path

import sys

from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT / 'backend'))

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal, engine
from app.models.artifact import Artifact, ArtifactRarity
from app.models.branch import Branch, BranchMission
from app.models.mission import Mission, MissionCompetencyReward, MissionDifficulty
from app.models.rank import Rank, RankCompetencyRequirement, RankMissionRequirement
from app.models.store import StoreItem
from app.models.user import Competency, CompetencyCategory, User, UserCompetency, UserRole

DATA_SENTINEL = settings.sqlite_path.parent / ".seeded"


def ensure_database() -> None:
    """Создаём таблицы, если их ещё нет."""

    from app.models.base import Base

    Base.metadata.create_all(bind=engine)


def seed() -> None:
    if DATA_SENTINEL.exists():
        print("Database already seeded, skipping")
        return

    ensure_database()

    session: Session = SessionLocal()
    try:
        # Компетенции
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

        # Ранги
        ranks = [
            Rank(title="Искатель", description="Первое знакомство с космофлотом", required_xp=0),
            Rank(title="Пилот-кандидат", description="Готовится к старту", required_xp=200),
            Rank(title="Член экипажа", description="Активно выполняет миссии", required_xp=500),
        ]
        session.add_all(ranks)
        session.flush()

        # Артефакты
        artifacts = [
            Artifact(
                name="Значок Буран",
                description="Памятный знак о легендарном корабле",
                rarity=ArtifactRarity.RARE,
            ),
            Artifact(
                name="Патч экипажа",
                description="Показывает принадлежность к команде",
                rarity=ArtifactRarity.COMMON,
            ),
        ]
        session.add_all(artifacts)
        session.flush()

        # Ветка миссий
        branch = Branch(
            title="Получение оффера",
            description="Путь кандидата от знакомства до выхода на орбиту",
            category="quest",
        )
        session.add(branch)
        session.flush()

        # Миссии
        mission_documents = Mission(
            title="Загрузка документов",
            description="Соберите полный пакет документов для HR",
            xp_reward=100,
            mana_reward=50,
            difficulty=MissionDifficulty.EASY,
            minimum_rank_id=ranks[0].id,
            artifact_id=artifacts[1].id,
        )
        mission_resume = Mission(
            title="Резюме астронавта",
            description="Обновите резюме с акцентом на космический опыт",
            xp_reward=120,
            mana_reward=60,
            difficulty=MissionDifficulty.MEDIUM,
            minimum_rank_id=ranks[0].id,
        )
        mission_interview = Mission(
            title="Собеседование с капитаном",
            description="Пройдите собеседование и докажите готовность",
            xp_reward=180,
            mana_reward=80,
            difficulty=MissionDifficulty.MEDIUM,
            minimum_rank_id=ranks[1].id,
            artifact_id=artifacts[0].id,
        )
        mission_onboarding = Mission(
            title="Онбординг экипажа",
            description="Познакомьтесь с кораблём и командой",
            xp_reward=200,
            mana_reward=100,
            difficulty=MissionDifficulty.HARD,
            minimum_rank_id=ranks[1].id,
        )
        session.add_all([mission_documents, mission_resume, mission_interview, mission_onboarding])
        session.flush()

        session.add_all(
            [
                MissionCompetencyReward(
                    mission_id=mission_documents.id,
                    competency_id=competencies[1].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_resume.id,
                    competency_id=competencies[0].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_interview.id,
                    competency_id=competencies[1].id,
                    level_delta=1,
                ),
                MissionCompetencyReward(
                    mission_id=mission_onboarding.id,
                    competency_id=competencies[3].id,
                    level_delta=1,
                ),
            ]
        )

        session.add_all(
            [
                BranchMission(branch_id=branch.id, mission_id=mission_documents.id, order=1),
                BranchMission(branch_id=branch.id, mission_id=mission_resume.id, order=2),
                BranchMission(branch_id=branch.id, mission_id=mission_interview.id, order=3),
                BranchMission(branch_id=branch.id, mission_id=mission_onboarding.id, order=4),
            ]
        )

        session.add_all(
            [
                RankMissionRequirement(rank_id=ranks[1].id, mission_id=mission_documents.id),
                RankMissionRequirement(rank_id=ranks[1].id, mission_id=mission_resume.id),
                RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_interview.id),
                RankMissionRequirement(rank_id=ranks[2].id, mission_id=mission_onboarding.id),
            ]
        )

        session.add_all(
            [
                RankCompetencyRequirement(
                    rank_id=ranks[1].id,
                    competency_id=competencies[1].id,
                    required_level=1,
                ),
                RankCompetencyRequirement(
                    rank_id=ranks[2].id,
                    competency_id=competencies[3].id,
                    required_level=1,
                ),
            ]
        )

        # Магазин
        session.add_all(
            [
                StoreItem(
                    name="Экскурсия по космодрому",
                    description="Личный тур по цехам Алабуги",
                    cost_mana=200,
                    stock=5,
                ),
                StoreItem(
                    name="Мерч экипажа",
                    description="Футболка с эмблемой миссии",
                    cost_mana=150,
                    stock=10,
                ),
            ]
        )

        # Пользователи
        pilot = User(
            email="candidate@alabuga.space",
            full_name="Алексей Пилотов",
            role=UserRole.PILOT,
            hashed_password=get_password_hash("orbita123"),
            current_rank_id=ranks[0].id,
        )
        hr = User(
            email="hr@alabuga.space",
            full_name="Мария HR",
            role=UserRole.HR,
            hashed_password=get_password_hash("orbita123"),
            current_rank_id=ranks[2].id,
        )
        session.add_all([pilot, hr])
        session.flush()

        session.add_all(
            [
                UserCompetency(user_id=pilot.id, competency_id=competencies[1].id, level=1),
                UserCompetency(user_id=pilot.id, competency_id=competencies[0].id, level=1),
            ]
        )

        session.commit()
        DATA_SENTINEL.write_text("seeded")
        print("Seed data created")
    finally:
        session.close()


if __name__ == "__main__":
    seed()

"""Проверяем повышение ранга."""

from __future__ import annotations

from app.models.mission import Mission, MissionSubmission, SubmissionStatus
from app.models.rank import Rank, RankMissionRequirement
from app.models.user import User, UserRole
from app.services.rank import apply_rank_upgrade


def test_rank_upgrade_after_requirements(db_session):
    """Пользователь получает ранг после выполнения условий."""

    novice = Rank(title="Новичок", description="Старт", required_xp=0)
    pilot = Rank(title="Пилот", description="Готов к полёту", required_xp=100)
    mission = Mission(title="Тренировка", description="Базовое обучение", xp_reward=100, mana_reward=0)

    db_session.add_all([novice, pilot, mission])
    db_session.flush()

    user = User(
        email="test@alabuga.space",
        full_name="Тестовый Пилот",
        role=UserRole.PILOT,
        hashed_password="hash",
        xp=120,
        current_rank_id=novice.id,
    )
    db_session.add(user)
    db_session.flush()

    submission = MissionSubmission(
        user_id=user.id,
        mission_id=mission.id,
        status=SubmissionStatus.APPROVED,
        awarded_xp=mission.xp_reward,
        awarded_mana=mission.mana_reward,
    )
    requirement = RankMissionRequirement(rank_id=pilot.id, mission_id=mission.id)

    db_session.add_all([user, submission, requirement])
    db_session.commit()
    db_session.refresh(user)

    new_rank = apply_rank_upgrade(user, db_session)

    assert new_rank is not None
    assert user.current_rank_id == pilot.id

"""Проверяем повышение ранга."""

from __future__ import annotations

from app.models.mission import Mission, MissionSubmission, SubmissionStatus
from app.models.rank import Rank, RankCompetencyRequirement, RankMissionRequirement
from app.models.user import Competency, CompetencyCategory, User, UserCompetency, UserRole
from app.services.rank import apply_rank_upgrade, build_progress_snapshot


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


def test_progress_snapshot_highlights_remaining_conditions(db_session):
    """Снэпшот прогресса показывает, что ещё нужно закрыть."""

    novice = Rank(title="Новичок", description="Старт", required_xp=0)
    pilot = Rank(title="Пилот", description="Готов к полёту", required_xp=100)
    mission = Mission(title="Тренировка", description="Базовое обучение", xp_reward=40, mana_reward=0)
    competency = Competency(
        name="Коммуникация",
        description="Чёткая передача информации",
        category=CompetencyCategory.COMMUNICATION,
    )

    db_session.add_all([novice, pilot, mission, competency])
    db_session.flush()

    db_session.add_all(
        [
            RankMissionRequirement(rank_id=pilot.id, mission_id=mission.id),
            RankCompetencyRequirement(
                rank_id=pilot.id,
                competency_id=competency.id,
                required_level=1,
            ),
        ]
    )

    user = User(
        email="progress@alabuga.space",
        full_name="Прогресс Тест",
        role=UserRole.PILOT,
        hashed_password="hash",
        xp=60,
        current_rank_id=novice.id,
    )
    db_session.add(user)
    db_session.flush()

    db_session.add(UserCompetency(user_id=user.id, competency_id=competency.id, level=0))
    db_session.commit()
    db_session.refresh(user)

    snapshot = build_progress_snapshot(user, db_session)

    assert snapshot.next_rank and snapshot.next_rank.title == "Пилот"
    assert snapshot.xp.remaining == 40
    assert snapshot.completed_missions == 0
    assert snapshot.total_missions == 1
    assert snapshot.met_competencies == 0
    assert snapshot.total_competencies == 1

    submission = MissionSubmission(
        user_id=user.id,
        mission_id=mission.id,
        status=SubmissionStatus.APPROVED,
        awarded_xp=mission.xp_reward,
    )
    user.xp = 120
    user_competency = user.competencies[0]
    user_competency.level = 2

    db_session.add_all([submission, user, user_competency])
    db_session.commit()
    db_session.refresh(user)

    snapshot_after = build_progress_snapshot(user, db_session)

    assert snapshot_after.completed_missions == snapshot_after.total_missions
    assert snapshot_after.met_competencies == snapshot_after.total_competencies
    assert snapshot_after.xp.remaining == 0

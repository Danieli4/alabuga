"""Тестируем отправку миссии."""

from __future__ import annotations

from app.models.artifact import Artifact, ArtifactRarity
from app.models.mission import Mission, MissionSubmission, SubmissionStatus
from app.models.user import User, UserRole
from app.services.mission import approve_submission


def test_approve_submission_rewards(db_session):
    """После одобрения пилот получает награды."""

    mission = Mission(title="Сборка спутника", description="Практика", xp_reward=150, mana_reward=90)
    user = User(
        email="pilot@alabuga.space",
        full_name="Пилот",
        role=UserRole.PILOT,
        hashed_password="hash",
    )

    db_session.add_all([mission, user])
    db_session.flush()

    submission = MissionSubmission(user_id=user.id, mission_id=mission.id)
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)
    db_session.refresh(user)

    approve_submission(db_session, submission)
    db_session.refresh(user)

    assert user.xp == mission.xp_reward
    assert user.mana == mission.mana_reward
    assert submission.status == SubmissionStatus.APPROVED


def test_approve_submission_grants_artifact(db_session):
    """При наличии артефакта пользователь получает его единожды."""

    artifact = Artifact(
        name="Значок испытателя",
        description="Выдан за успешную миссию",
        rarity=ArtifactRarity.RARE,
    )
    mission = Mission(
        title="Тестовая миссия",
        description="Описание",
        xp_reward=50,
        mana_reward=20,
        artifact=artifact,
    )
    user = User(
        email="artifact@alabuga.space",
        full_name="Пилот",
        role=UserRole.PILOT,
        hashed_password="hash",
    )
    db_session.add_all([artifact, mission, user])
    db_session.flush()

    submission = MissionSubmission(user_id=user.id, mission_id=mission.id)
    db_session.add(submission)
    db_session.commit()
    db_session.refresh(submission)

    approve_submission(db_session, submission)
    db_session.refresh(user)

    assert len(user.artifacts) == 1
    assert user.artifacts[0].artifact_id == artifact.id

    # Повторное одобрение не создаёт дубли
    approve_submission(db_session, submission)
    db_session.refresh(user)
    assert len(user.artifacts) == 1

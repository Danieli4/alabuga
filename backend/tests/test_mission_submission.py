"""Тестируем отправку миссии."""

from __future__ import annotations

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

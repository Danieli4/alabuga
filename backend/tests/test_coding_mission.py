"""Проверяем автоматические миссии на Python."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.models.coding import CodingChallenge
from app.models.mission import Mission, MissionDifficulty, MissionSubmission, SubmissionStatus
from app.models.user import User, UserRole
from app.services.coding import count_completed_challenges, evaluate_challenge


def _create_user(db_session) -> User:
    user = User(
        email="python@alabuga.space",
        full_name="Python Pilot",
        role=UserRole.PILOT,
        hashed_password="hash",
    )
    db_session.add(user)
    db_session.flush()
    return user


def _create_mission_with_challenges(db_session) -> tuple[Mission, list[CodingChallenge]]:
    mission = Mission(
        title="Учебная миссия",
        description="Две задачи на программирование",
        xp_reward=120,
        mana_reward=60,
        difficulty=MissionDifficulty.MEDIUM,
    )
    challenge_one = CodingChallenge(
        mission=mission,
        order=1,
        title="Приветствие",
        prompt="Выведите Привет",
        starter_code="",
        expected_output="Привет",
    )
    challenge_two = CodingChallenge(
        mission=mission,
        order=2,
        title="Пока",
        prompt="Выведите Пока",
        starter_code="",
        expected_output="Пока",
    )
    db_session.add_all([mission, challenge_one, challenge_two])
    db_session.flush()
    return mission, [challenge_one, challenge_two]


def test_challenges_require_sequential_completion(db_session):
    """Нельзя переходить к следующему заданию без успешного выполнения предыдущего."""

    mission, (challenge_one, challenge_two) = _create_mission_with_challenges(db_session)
    user = _create_user(db_session)

    with pytest.raises(HTTPException):
        evaluate_challenge(db_session, challenge=challenge_two, user=user, code="print('Пока')")

    first_attempt = evaluate_challenge(db_session, challenge=challenge_one, user=user, code="print('Привет')")
    assert first_attempt.attempt.is_passed is True
    assert first_attempt.mission_completed is False

    second_attempt = evaluate_challenge(db_session, challenge=challenge_two, user=user, code="print('Пока')")
    assert second_attempt.attempt.is_passed is True
    assert second_attempt.mission_completed is True

    db_session.refresh(user)
    assert user.xp == mission.xp_reward
    assert user.mana == mission.mana_reward

    submission = (
        db_session.query(MissionSubmission)
        .filter(MissionSubmission.user_id == user.id, MissionSubmission.mission_id == mission.id)
        .first()
    )
    assert submission is not None
    assert submission.status == SubmissionStatus.APPROVED


def test_failed_attempt_does_not_unlock_next_challenge(db_session):
    """Неудачные запуски фиксируются, но не засчитываются как выполненные."""

    mission, (challenge_one, challenge_two) = _create_mission_with_challenges(db_session)
    user = _create_user(db_session)

    failed = evaluate_challenge(db_session, challenge=challenge_one, user=user, code="print('Не то')")
    assert failed.attempt.is_passed is False
    assert failed.mission_completed is False

    progress = count_completed_challenges(db_session, mission_ids=[mission.id], user=user)
    assert progress.get(mission.id, 0) == 0

    with pytest.raises(HTTPException):
        evaluate_challenge(db_session, challenge=challenge_two, user=user, code="print('Пока')")

    evaluate_challenge(db_session, challenge=challenge_one, user=user, code="print('Привет')")
    progress = count_completed_challenges(db_session, mission_ids=[mission.id], user=user)
    assert progress.get(mission.id, 0) == 1

    follow_up = evaluate_challenge(db_session, challenge=challenge_two, user=user, code="print('Пока')")
    assert follow_up.attempt.is_passed is True


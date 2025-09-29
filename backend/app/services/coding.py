"""Сервисные функции для миссии с заданиями на программирование."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.coding import CodingAttempt, CodingChallenge
from app.models.mission import Mission, MissionSubmission, SubmissionStatus
from app.models.user import User
from app.services.mission import approve_submission
from app.utils.python_runner import PythonRunResult, run_user_python_code


@dataclass(slots=True)
class AttemptEvaluation:
    """Результат проверки решения."""

    attempt: CodingAttempt
    mission_completed: bool


def _normalize_output(raw: str) -> str:
    """Удаляем завершающие перевод строки и приводим переносы к ``\n``."""

    return raw.replace("\r\n", "\n").rstrip("\n")


def _ensure_previous_challenges_solved(
    db: Session,
    *,
    challenge: CodingChallenge,
    user: User,
) -> None:
    """Проверяем, что все предыдущие задания завершены."""

    previous_ids = (
        db.execute(
            select(CodingChallenge.id)
            .where(
                CodingChallenge.mission_id == challenge.mission_id,
                CodingChallenge.order < challenge.order,
            )
            .order_by(CodingChallenge.order)
        )
        .scalars()
        .all()
    )

    if not previous_ids:
        return

    solved_ids = set(
        db.execute(
            select(CodingAttempt.challenge_id)
            .where(
                CodingAttempt.user_id == user.id,
                CodingAttempt.challenge_id.in_(previous_ids),
                CodingAttempt.is_passed.is_(True),
            )
            .distinct()
        )
        .scalars()
        .all()
    )

    missing = [challenge_id for challenge_id in previous_ids if challenge_id not in solved_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сначала решите предыдущие задачи этой миссии.",
        )


def _finalize_mission_if_needed(
    db: Session,
    *,
    mission: Mission,
    user: User,
    challenge_ids: Iterable[int],
) -> bool:
    """Если пилот решил все задания, автоматически засчитываем миссию."""

    challenge_ids = list(challenge_ids)
    if not challenge_ids:
        return False

    solved_ids = set(
        db.execute(
            select(CodingAttempt.challenge_id)
            .where(
                CodingAttempt.user_id == user.id,
                CodingAttempt.challenge_id.in_(challenge_ids),
                CodingAttempt.is_passed.is_(True),
            )
            .distinct()
        )
        .scalars()
        .all()
    )

    if len(solved_ids) != len(set(challenge_ids)):
        return False

    submission = (
        db.query(MissionSubmission)
        .filter(
            MissionSubmission.user_id == user.id,
            MissionSubmission.mission_id == mission.id,
        )
        .first()
    )

    if not submission:
        submission = MissionSubmission(user_id=user.id, mission_id=mission.id)
        db.add(submission)
        db.flush()
        db.refresh(submission)

    if submission.status == SubmissionStatus.APPROVED:
        return True

    submission.comment = "Автоматическая проверка: все задания решены."
    db.add(submission)
    db.flush()
    db.refresh(submission)
    approve_submission(db, submission)
    return True


def evaluate_challenge(
    db: Session,
    *,
    challenge: CodingChallenge,
    user: User,
    code: str,
) -> AttemptEvaluation:
    """Запускаем код пользователя и сохраняем попытку."""

    _ensure_previous_challenges_solved(db, challenge=challenge, user=user)

    run_result: PythonRunResult = run_user_python_code(code)
    expected = _normalize_output(challenge.expected_output)
    actual = _normalize_output(run_result.stdout)

    is_passed = run_result.exit_code == 0 and actual == expected

    attempt = CodingAttempt(
        challenge_id=challenge.id,
        user_id=user.id,
        code=code,
        stdout=run_result.stdout,
        stderr=run_result.stderr,
        exit_code=run_result.exit_code,
        is_passed=is_passed,
    )

    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    mission = challenge.mission or db.query(Mission).filter(Mission.id == challenge.mission_id).first()
    mission_completed = False

    if is_passed and mission:
        mission_completed = _finalize_mission_if_needed(
            db,
            mission=mission,
            user=user,
            challenge_ids=[item.id for item in mission.coding_challenges],
        )

    return AttemptEvaluation(attempt=attempt, mission_completed=mission_completed)


def count_completed_challenges(db: Session, *, mission_ids: Iterable[int], user: User) -> dict[int, int]:
    """Возвращаем количество решённых заданий по миссиям."""

    mission_ids = list(mission_ids)
    if not mission_ids:
        return {}

    rows = db.execute(
        select(CodingChallenge.mission_id, func.count(func.distinct(CodingChallenge.id)))
        .join(
            CodingAttempt,
            and_(
                CodingAttempt.challenge_id == CodingChallenge.id,
                CodingAttempt.user_id == user.id,
                CodingAttempt.is_passed.is_(True),
            ),
        )
        .where(CodingChallenge.mission_id.in_(mission_ids))
        .group_by(CodingChallenge.mission_id)
    ).all()

    return {mission_id: count for mission_id, count in rows}


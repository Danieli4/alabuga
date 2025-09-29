"""Логика миссии по Python."""

from __future__ import annotations

import subprocess
import sys
from datetime import datetime
from textwrap import dedent
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.mission import Mission, MissionSubmission
from app.models.python import PythonChallenge, PythonSubmission, PythonUserProgress
from app.models.user import User
from app.schemas.python import PythonMissionState, PythonChallengeRead, PythonSubmissionRead
from app.services.mission import submit_mission

EVAL_TIMEOUT_SECONDS = 3


def _normalize_stdout(value: str | None) -> str:
    if value is None:
        return ""
    return value.replace('\r\n', '\n').rstrip('\n').strip()


def get_progress(db: Session, user: User, mission: Mission) -> PythonUserProgress:
    progress = (
        db.query(PythonUserProgress)
        .filter(PythonUserProgress.user_id == user.id, PythonUserProgress.mission_id == mission.id)
        .first()
    )
    if not progress:
        progress = PythonUserProgress(user_id=user.id, mission_id=mission.id, current_order=0)
        db.add(progress)
        db.commit()
        db.refresh(progress)
    return progress


def build_state(db: Session, user: User, mission: Mission) -> PythonMissionState:
    progress = get_progress(db, user, mission)
    challenges = (
        db.query(PythonChallenge)
        .filter(PythonChallenge.mission_id == mission.id)
        .order_by(PythonChallenge.order)
        .all()
    )
    total = len(challenges)
    completed = progress.current_order

    next_challenge: Optional[PythonChallenge] = None
    last_code: Optional[str] = None
    last_submissions: list[PythonSubmission] = []

    if completed < total:
        next_challenge = challenges[completed]
        last_submission = (
            db.query(PythonSubmission)
            .filter(
                PythonSubmission.progress_id == progress.id,
                PythonSubmission.challenge_id == next_challenge.id,
            )
            .order_by(PythonSubmission.created_at.desc())
            .first()
        )
        if last_submission:
            last_code = last_submission.code
    else:
        last_submission = (
            db.query(PythonSubmission)
            .filter(PythonSubmission.progress_id == progress.id)
            .order_by(PythonSubmission.created_at.desc())
            .first()
        )
        if last_submission:
            last_code = last_submission.code

    last_submissions = (
        db.query(PythonSubmission)
        .filter(PythonSubmission.progress_id == progress.id)
        .order_by(PythonSubmission.created_at.desc())
        .limit(5)
        .all()
    )

    return PythonMissionState(
        mission_id=mission.id,
        total_challenges=total,
        completed_challenges=completed,
        is_completed=completed >= total,
        next_challenge=PythonChallengeRead.model_validate(next_challenge) if next_challenge else None,
        last_submissions=[PythonSubmissionRead.model_validate(item) for item in last_submissions],
        last_code=last_code,
    )


def submit_code(db: Session, user: User, mission: Mission, challenge_id: int, code: str) -> PythonSubmission:
    progress = get_progress(db, user, mission)

    challenge = (
        db.query(PythonChallenge)
        .filter(PythonChallenge.id == challenge_id, PythonChallenge.mission_id == mission.id)
        .first()
    )
    if not challenge:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Задание не найдено")

    expected_order = progress.current_order + 1
    if challenge.order != expected_order:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сначала выполните предыдущее задание",
        )

    prepared_code = dedent(code)

    try:
        completed = subprocess.run(
            [sys.executable, "-c", prepared_code],
            input=(challenge.input_data or ""),
            capture_output=True,
            text=True,
            timeout=EVAL_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Время выполнения превышено")

    stdout = completed.stdout or ""
    stderr = completed.stderr or ""

    expected = _normalize_stdout(challenge.expected_output)
    actual = _normalize_stdout(stdout)

    is_passed = completed.returncode == 0 and actual == expected

    submission = PythonSubmission(
        progress_id=progress.id,
        challenge_id=challenge.id,
        code=prepared_code,
        stdout=stdout,
        stderr=stderr,
        is_passed=is_passed,
    )
    db.add(submission)

    if is_passed:
        progress.current_order = challenge.order
        total = (
            db.query(PythonChallenge)
            .filter(PythonChallenge.mission_id == mission.id)
            .count()
        )
        if progress.current_order >= total:
            progress.completed_at = datetime.utcnow()
            ensure_mission_completed(db, user, mission)

    db.commit()
    db.refresh(submission)
    db.refresh(progress)
    return submission


def ensure_mission_completed(db: Session, user: User, mission: Mission) -> None:
    existing_submission = (
        db.query(MissionSubmission)
        .filter(MissionSubmission.user_id == user.id, MissionSubmission.mission_id == mission.id)
        .first()
    )
    if existing_submission and existing_submission.status.value == "approved":
        return

    submit_mission(
        db=db,
        user=user,
        mission=mission,
        comment="Задачи Python-миссии решены",
        proof_url=None,
    )

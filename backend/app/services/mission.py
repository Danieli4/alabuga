"""Бизнес-логика работы с миссиями."""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.journal import JournalEventType
from app.models.mission import Mission, MissionSubmission, SubmissionStatus
from app.models.user import User, UserCompetency
from app.services.journal import log_event
from app.services.rank import apply_rank_upgrade


def submit_mission(
    *, db: Session, user: User, mission: Mission, comment: str | None, proof_url: str | None
) -> MissionSubmission:
    """Создаём или обновляем отправку."""

    submission = (
        db.query(MissionSubmission)
        .filter(MissionSubmission.user_id == user.id, MissionSubmission.mission_id == mission.id)
        .first()
    )
    if submission and submission.status == SubmissionStatus.APPROVED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Миссия уже зачтена")

    if not submission:
        submission = MissionSubmission(user_id=user.id, mission_id=mission.id)

    submission.comment = comment
    submission.proof_url = proof_url
    submission.status = SubmissionStatus.PENDING

    db.add(submission)
    db.commit()
    db.refresh(submission)

    log_event(
        db,
        user_id=user.id,
        event_type=JournalEventType.MISSION_COMPLETED,
        title=f"Отправка миссии «{mission.title}»",
        description="Отчёт отправлен и ожидает проверки.",
        payload={"mission_id": mission.id},
    )

    return submission


def _increase_competencies(db: Session, user: User, mission: Mission) -> None:
    """Повышаем уровни компетенций за миссию."""

    for reward in mission.competency_rewards:
        user_competency = next(
            (uc for uc in user.competencies if uc.competency_id == reward.competency_id),
            None,
        )
        if not user_competency:
            user_competency = UserCompetency(
                user_id=user.id, competency_id=reward.competency_id, level=0
            )
            db.add(user_competency)
            db.flush()
        user_competency.level += reward.level_delta
        db.add(user_competency)


def approve_submission(db: Session, submission: MissionSubmission) -> MissionSubmission:
    """Подтверждаем миссию, начисляем награды и проверяем ранг."""

    if submission.status == SubmissionStatus.APPROVED:
        return submission

    submission.status = SubmissionStatus.APPROVED
    submission.awarded_xp = submission.mission.xp_reward
    submission.awarded_mana = submission.mission.mana_reward

    user = submission.user
    user.xp += submission.awarded_xp
    user.mana += submission.awarded_mana

    _increase_competencies(db, user, submission.mission)

    db.add_all([submission, user])
    db.commit()
    db.refresh(submission)

    log_event(
        db,
        user_id=user.id,
        event_type=JournalEventType.MISSION_COMPLETED,
        title=f"Миссия «{submission.mission.title}» подтверждена",
        description="HR одобрил выполнение миссии.",
        payload={"mission_id": submission.mission_id},
        xp_delta=submission.awarded_xp,
        mana_delta=submission.awarded_mana,
    )

    apply_rank_upgrade(user, db)

    return submission


def reject_submission(db: Session, submission: MissionSubmission, comment: str | None = None) -> MissionSubmission:
    """Отклоняем миссию."""

    submission.status = SubmissionStatus.REJECTED
    if comment:
        submission.comment = comment
    db.add(submission)
    db.commit()
    db.refresh(submission)

    log_event(
        db,
        user_id=submission.user_id,
        event_type=JournalEventType.MISSION_COMPLETED,
        title=f"Миссия «{submission.mission.title}» отклонена",
        description=comment or "Проверьте отчёт и отправьте снова.",
        payload={"mission_id": submission.mission_id},
    )

    return submission
